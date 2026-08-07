"""
DynamoDB persistence layer for Wage Card Management System.
Supports both local DynamoDB and AWS DynamoDB.
Falls back to in-memory storage if DynamoDB is unavailable.
"""

import os
import uuid
import json
from datetime import datetime
from typing import Optional
import boto3
from botocore.exceptions import ClientError, NoCredentialsError, EndpointConnectionError


# Configuration
DYNAMODB_TABLE_PREFIX = os.environ.get("DYNAMODB_TABLE_PREFIX", "WageCard")
AWS_REGION = os.environ.get("AWS_REGION", "ap-south-1")
DYNAMODB_ENDPOINT = os.environ.get("DYNAMODB_ENDPOINT", None)  # For local dev

# Table names
WAGE_CARDS_TABLE = f"{DYNAMODB_TABLE_PREFIX}_WageCards"
MINIMUM_WAGES_TABLE = f"{DYNAMODB_TABLE_PREFIX}_MinimumWages"
AUDIT_LOG_TABLE = f"{DYNAMODB_TABLE_PREFIX}_AuditLog"
CONFIG_TABLE = f"{DYNAMODB_TABLE_PREFIX}_Config"


def get_dynamodb_resource():
    """Get DynamoDB resource, supporting local endpoint."""
    kwargs = {"region_name": AWS_REGION}
    if DYNAMODB_ENDPOINT:
        kwargs["endpoint_url"] = DYNAMODB_ENDPOINT
    return boto3.resource("dynamodb", **kwargs)


def get_dynamodb_client():
    """Get DynamoDB client."""
    kwargs = {"region_name": AWS_REGION}
    if DYNAMODB_ENDPOINT:
        kwargs["endpoint_url"] = DYNAMODB_ENDPOINT
    return boto3.client("dynamodb", **kwargs)


class DynamoDBStore:
    """DynamoDB-backed storage with file-based fallback for persistence."""

    def __init__(self):
        self.use_dynamo = False
        self._data_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'data.json')
        self._memory_store: dict[str, dict[str, dict]] = {
            "wage_cards": {},
            "minimum_wages": {},
            "audit_log": {},
            "config": {},
        }

        # Try to load persisted data from file
        self._load_from_file()

        try:
            self.dynamodb = get_dynamodb_resource()
            self.client = get_dynamodb_client()
            # Test connection
            self.client.list_tables(Limit=1)
            self.use_dynamo = True
            self._ensure_tables()
            print("✅ Connected to DynamoDB")
        except (NoCredentialsError, EndpointConnectionError, ClientError) as e:
            print(f"⚠️ DynamoDB unavailable, using file-based storage ({self._data_file})")
            self.use_dynamo = False

    def _load_from_file(self):
        """Load persisted data from JSON file."""
        try:
            if os.path.exists(self._data_file):
                with open(self._data_file, 'r') as f:
                    data = json.load(f)
                    self._memory_store = data
                    count = len(data.get("wage_cards", {}))
                    if count > 0:
                        print(f"✅ Loaded {count} wage cards from saved data")
        except Exception as e:
            print(f"⚠️ Could not load saved data: {e}")

    def _save_to_file(self):
        """Persist data to JSON file."""
        try:
            os.makedirs(os.path.dirname(self._data_file), exist_ok=True)
            with open(self._data_file, 'w') as f:
                json.dump(self._memory_store, f)
        except Exception as e:
            print(f"⚠️ Could not save data: {e}")

    def _ensure_tables(self):
        """Create tables if they don't exist."""
        existing = self.client.list_tables()["TableNames"]

        tables_to_create = [
            {
                "name": WAGE_CARDS_TABLE,
                "key_schema": [{"AttributeName": "id", "KeyType": "HASH"}],
                "attributes": [{"AttributeName": "id", "AttributeType": "S"}],
            },
            {
                "name": MINIMUM_WAGES_TABLE,
                "key_schema": [
                    {"AttributeName": "state_city_zone_skill", "KeyType": "HASH"},
                    {"AttributeName": "effective_date", "KeyType": "RANGE"},
                ],
                "attributes": [
                    {"AttributeName": "state_city_zone_skill", "AttributeType": "S"},
                    {"AttributeName": "effective_date", "AttributeType": "S"},
                ],
            },
            {
                "name": AUDIT_LOG_TABLE,
                "key_schema": [
                    {"AttributeName": "entity_id", "KeyType": "HASH"},
                    {"AttributeName": "timestamp", "KeyType": "RANGE"},
                ],
                "attributes": [
                    {"AttributeName": "entity_id", "AttributeType": "S"},
                    {"AttributeName": "timestamp", "AttributeType": "S"},
                ],
            },
            {
                "name": CONFIG_TABLE,
                "key_schema": [{"AttributeName": "config_key", "KeyType": "HASH"}],
                "attributes": [{"AttributeName": "config_key", "AttributeType": "S"}],
            },
        ]

        for table_def in tables_to_create:
            if table_def["name"] not in existing:
                try:
                    self.client.create_table(
                        TableName=table_def["name"],
                        KeySchema=table_def["key_schema"],
                        AttributeDefinitions=table_def["attributes"],
                        BillingMode="PAY_PER_REQUEST",
                    )
                    print(f"  Created table: {table_def['name']}")
                except ClientError as e:
                    if e.response["Error"]["Code"] != "ResourceInUseException":
                        raise

    # =========================================================================
    # WAGE CARDS
    # =========================================================================

    def put_wage_card(self, card: dict, skip_save: bool = False) -> dict:
        """Store a wage card. Use skip_save=True for bulk operations, then call save() manually."""
        if not card.get("id"):
            card["id"] = str(uuid.uuid4())

        card["updated_at"] = datetime.utcnow().isoformat()
        if not card.get("created_at"):
            card["created_at"] = card["updated_at"]

        if self.use_dynamo:
            table = self.dynamodb.Table(WAGE_CARDS_TABLE)
            # DynamoDB doesn't support float, convert to Decimal-safe format
            clean_card = self._clean_for_dynamo(card)
            table.put_item(Item=clean_card)
        else:
            self._memory_store["wage_cards"][card["id"]] = card
            if not skip_save:
                self._save_to_file()

        return card

    def save(self):
        """Manually trigger a save (use after bulk operations)."""
        if not self.use_dynamo:
            self._save_to_file()

    def get_wage_card(self, card_id: str) -> Optional[dict]:
        """Get a wage card by ID."""
        if self.use_dynamo:
            table = self.dynamodb.Table(WAGE_CARDS_TABLE)
            try:
                response = table.get_item(Key={"id": card_id})
                item = response.get("Item")
                return self._clean_from_dynamo(item) if item else None
            except ClientError:
                return None
        else:
            return self._memory_store["wage_cards"].get(card_id)

    def list_wage_cards(self, filters: dict = None) -> list[dict]:
        """List wage cards with optional filters."""
        if self.use_dynamo:
            table = self.dynamodb.Table(WAGE_CARDS_TABLE)
            response = table.scan()
            items = [self._clean_from_dynamo(i) for i in response.get("Items", [])]
        else:
            items = list(self._memory_store["wage_cards"].values())

        # Apply filters
        if filters:
            if filters.get("state"):
                items = [i for i in items if i.get("state", "").upper() == filters["state"].upper()]
            if filters.get("city"):
                items = [i for i in items if i.get("city", "").upper() == filters["city"].upper()]
            if filters.get("business_title"):
                items = [i for i in items if i.get("business_title", "").upper() == filters["business_title"].upper()]
            if filters.get("tenure_years") is not None:
                items = [i for i in items if i.get("tenure_years") == filters["tenure_years"]]

        return items

    def delete_wage_card(self, card_id: str) -> bool:
        """Delete a wage card."""
        if self.use_dynamo:
            table = self.dynamodb.Table(WAGE_CARDS_TABLE)
            try:
                table.delete_item(Key={"id": card_id})
                return True
            except ClientError:
                return False
        else:
            if card_id in self._memory_store["wage_cards"]:
                del self._memory_store["wage_cards"][card_id]
                self._save_to_file()
                return True
            return False

    # =========================================================================
    # MINIMUM WAGES
    # =========================================================================

    def put_minimum_wage(self, mw: dict) -> dict:
        """Store a minimum wage entry."""
        key = f"{mw['state']}#{mw['city']}#{mw.get('mw_zone', 'A')}#{mw['skill_category']}"
        mw["state_city_zone_skill"] = key

        if self.use_dynamo:
            table = self.dynamodb.Table(MINIMUM_WAGES_TABLE)
            table.put_item(Item=self._clean_for_dynamo(mw))
        else:
            self._memory_store["minimum_wages"][f"{key}#{mw['effective_date']}"] = mw

        return mw

    def get_latest_minimum_wage(self, state: str, city: str, mw_zone: str, skill_category: str) -> Optional[dict]:
        """Get the latest minimum wage for a state/city/zone/skill."""
        key = f"{state}#{city}#{mw_zone}#{skill_category}"

        if self.use_dynamo:
            table = self.dynamodb.Table(MINIMUM_WAGES_TABLE)
            response = table.query(
                KeyConditionExpression="state_city_zone_skill = :key",
                ExpressionAttributeValues={":key": key},
                ScanIndexForward=False,
                Limit=1,
            )
            items = response.get("Items", [])
            return self._clean_from_dynamo(items[0]) if items else None
        else:
            matching = [
                v for k, v in self._memory_store["minimum_wages"].items()
                if k.startswith(key)
            ]
            if matching:
                return sorted(matching, key=lambda x: x.get("effective_date", ""), reverse=True)[0]
            return None

    # =========================================================================
    # AUDIT LOG
    # =========================================================================

    def put_audit_entry(self, entry: dict) -> dict:
        """Store an audit log entry."""
        if not entry.get("id"):
            entry["id"] = str(uuid.uuid4())
        entry["timestamp"] = entry.get("timestamp", datetime.utcnow().isoformat())

        if self.use_dynamo:
            table = self.dynamodb.Table(AUDIT_LOG_TABLE)
            table.put_item(Item=self._clean_for_dynamo(entry))
        else:
            self._memory_store["audit_log"][entry["id"]] = entry

        return entry

    def list_audit_entries(self, entity_id: str = None, limit: int = 50) -> list[dict]:
        """List audit log entries."""
        if self.use_dynamo:
            table = self.dynamodb.Table(AUDIT_LOG_TABLE)
            if entity_id:
                response = table.query(
                    KeyConditionExpression="entity_id = :eid",
                    ExpressionAttributeValues={":eid": entity_id},
                    ScanIndexForward=False,
                    Limit=limit,
                )
            else:
                response = table.scan(Limit=limit)
            return [self._clean_from_dynamo(i) for i in response.get("Items", [])]
        else:
            entries = list(self._memory_store["audit_log"].values())
            if entity_id:
                entries = [e for e in entries if e.get("entity_id") == entity_id]
            return sorted(entries, key=lambda x: x.get("timestamp", ""), reverse=True)[:limit]

    # =========================================================================
    # HELPERS
    # =========================================================================

    def _clean_for_dynamo(self, item: dict) -> dict:
        """Convert Python types to DynamoDB-compatible types."""
        from decimal import Decimal
        clean = {}
        for k, v in item.items():
            if v is None:
                continue
            elif isinstance(v, float):
                clean[k] = Decimal(str(v))
            elif isinstance(v, dict):
                clean[k] = self._clean_for_dynamo(v)
            elif isinstance(v, list):
                clean[k] = [self._clean_for_dynamo(i) if isinstance(i, dict) else i for i in v]
            else:
                clean[k] = v
        return clean

    def _clean_from_dynamo(self, item: dict) -> dict:
        """Convert DynamoDB types back to Python types."""
        from decimal import Decimal
        if item is None:
            return None
        clean = {}
        for k, v in item.items():
            if isinstance(v, Decimal):
                clean[k] = float(v)
            elif isinstance(v, dict):
                clean[k] = self._clean_from_dynamo(v)
            elif isinstance(v, list):
                clean[k] = [self._clean_from_dynamo(i) if isinstance(i, dict) else float(i) if isinstance(i, Decimal) else i for i in v]
            else:
                clean[k] = v
        return clean


# Singleton instance
db = DynamoDBStore()
