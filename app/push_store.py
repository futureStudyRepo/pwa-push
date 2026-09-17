import json
from pathlib import Path


class PushSubscriptionStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text("[]", encoding="utf-8")

    def all(self) -> list[dict]:
        return json.loads(self.path.read_text(encoding="utf-8"))

    def save_all(self, subscriptions: list[dict]) -> None:
        self.path.write_text(
            json.dumps(subscriptions, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def upsert(self, subscription: dict) -> None:
        subscriptions = self.all()
        endpoint = subscription.get("endpoint")
        found = False

        for index, existing in enumerate(subscriptions):
            if existing.get("endpoint") == endpoint:
                subscriptions[index] = subscription
                found = True
                break

        if not found:
            subscriptions.append(subscription)

        self.save_all(subscriptions)

    def remove_by_endpoint(self, endpoint: str) -> None:
        subscriptions = [item for item in self.all() if item.get("endpoint") != endpoint]
        self.save_all(subscriptions)
