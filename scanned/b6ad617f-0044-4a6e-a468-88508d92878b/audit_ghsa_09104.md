# [H] PraisonAI ships and generates a legacy API server with authentication disabled by default, allowing unauthenticated workflow execution

## Summary
Severity: High
Advisory: GHSA-6rmh-7xcm-cpxj
CVE: CVE-2026-44338
CWE: CWE-1188, CWE-306, CWE-668
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-05-11
Source: https://github.com/advisories/GHSA-6rmh-7xcm-cpxj
Type: github-advisory

## Affected
- PyPI: `PraisonAI` — affected >=2.5.6 <4.6.34

## Details
### Summary
PraisonAI ships a legacy Flask API server with authentication disabled by default. When that server is used, any caller that can reach it can access `/agents` and trigger the configured `agents.yaml` workflow through `/chat` without providing a token.

### Details
The vulnerable server is the shipped `src/praisonai/api_server.py` entrypoint.

- `AUTH_ENABLED = False` and `AUTH_TOKEN = None` are hard-coded at [[src/praisonai/api_server.py](https://github.com/Users/shmulc/Stuff/tmp/first-cve/scans/variant-hunt/PraisonAI/src/praisonai/api_server.py:15)](/Users/shmulc/Stuff/tmp/first-cve/scans/variant-hunt/PraisonAI/src/praisonai/api_server.py:15).
- `check_auth()` returns `True` whenever authentication is disabled, so both protected routes fail open by design at [[src/praisonai/api_server.py](https://github.com/Users/shmulc/Stuff/tmp/first-cve/scans/variant-hunt/PraisonAI/src/praisonai/api_server.py:18)](/Users/shmulc/Stuff/tmp/first-cve/scans/variant-hunt/PraisonAI/src/praisonai/api_server.py:18).
- `POST /chat` only checks that the request JSON contains a `message` key and then runs `PraisonAI(agent_file="agents.yaml").run()` at [[src/praisonai/api_server.py](https://github.com/Users/shmulc/Stuff/tmp/first-cve/scans/variant-hunt/PraisonAI/src/praisonai/api_server.py:31)](/Users/shmulc/Stuff/tmp/first-cve/scans/variant-hunt/PraisonAI/src/praisonai/api_server.py:31).
- `GET /agents` is guarded by the same no-op authentication check and returns agent metadata at [[src/praisonai/api_server.py](https://github.com/Users/shmulc/Stuff/tmp/first-cve/scans/variant-hunt/PraisonAI/src/praisonai/api_server.py:55)](/Users/shmulc/Stuff/tmp/first-cve/scans/variant-hunt/PraisonAI/[src/praisonai/api_server.py](https://github.com/Users/shmulc/Stuff/tmp/first-cve/scans/variant-hunt/PraisonAI/src/praisonai/api_server.py:66):55).
- When launched directly, the same script binds to `0.0.0.0:8080` at [src/praisonai/api_server.py](/Users/shmulc/Stuff/tmp/first-cve/scans/variant-hunt/PraisonAI/src/praisonai/api_server.py:66).

The deploy subsystem keeps the same insecure authentication default:

- `APIConfig` defaults `auth_enabled` to `False` in [[src/praisonai/praisonai/deploy/models.py](https://github.com/Users/shmulc/Stuff/tmp/first-cve/scans/variant-hunt/PraisonAI/src/praisonai/praisonai/deploy/models.py:23)](/Users/shmulc/Stuff/tmp/first-cve/scans/variant-hunt/PraisonAI/src/praisonai/praisonai/deploy/models.py:23).
- The generated sample API deployment YAML recommends `host: 0.0.0.0` together with `auth_enabled: false` in [[src/praisonai/praisonai/deploy/schema.py](https://github.com/Users/shmulc/Stuff/tmp/first-cve/scans/variant-hunt/PraisonAI/src/praisonai/praisonai/deploy/schema.py:108)](/Users/shmulc/Stuff/tmp/first-cve/scans/variant-hunt/PraisonAI/src/praisonai/praisonai/deploy/schema.py:108).

For scope clarity: the newer `serve agents` command is safer by default, because it binds to `127.0.0.1` and supports `--api-key` in [[src/praisonai/praisonai/cli/commands/serve.py](https://github.com/Users/shmulc/Stuff/tmp/first-cve/scans/variant-hunt/PraisonAI/src/praisonai/praisonai/cli/commands/serve.py:155)](/Users/shmulc/Stuff/tmp/first-cve/scans/variant-hunt/PraisonAI/src/praisonai/praisonai/cli/commands/serve.py:155). This report is about the shipped legacy API server and the generated/sample API deployment path above.

Version scope:

- `v2.5.6` already ships the same `src/praisonai/api_server.py` implementation.
- The current PyPI release on May 1, 2026 is `4.6.33`, and it still ships the same unauthenticated server logic.

### PoC
The following route-level reproduction was verified locally and proves that the shipped `api_server.py` exposes `/agents` and `/chat` without authentication.

1. From the repository root, create a throwaway environment with the server's direct Flask dependencies:

```bash
python3 -m venv /tmp/praisonai-ghsa-venv
/tmp/praisonai-ghsa-venv/bin/pip install flask flask-cors
```

2. Execute the shipped `src/praisonai/api_server.py` under a minimal stub for `praisonai.PraisonAI` so only the server auth logic is exercised:

```bash
/tmp/praisonai-ghsa-venv/bin/python - <<'PY'
import importlib.util
import pathlib
import sys
import types

stub = types.ModuleType("praisonai")

class DummyPraisonAI:
    def __init__(self, agent_file="agents.yaml"):
        self.agent_file = agent_file
    def run(self):
        return {"ran": True, "agent_file": self.agent_file}

stub.PraisonAI = DummyPraisonAI
sys.modules["praisonai"] = stub

path = pathlib.Path("src/praisonai/api_server.py").resolve()
spec = importlib.util.spec_from_file_location("api_server_local", path)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

client = mod.app.test_client()
print(client.get("/agents").status_code, client.get("/agents").get_data(as_text=True))
print(client.post("/chat", json={"message": "hello"}).status_code, client.post("/chat", json={"message": "hello"}).get_data(as_text=True))
PY
```

3. Observed result:

```text
200 {"agent_file":"agents.yaml","agents":["default"]}
200 {"response":{"agent_file":"agents.yaml","ran":true},"status":"success"}
```

Both endpoints succeed without any `Authorization` header.

### Impact
Any reachable caller can invoke the legacy API server's protected functionality without a token.

At minimum, this allows:

- unauthenticated enumeration of the configured agent file through `/agents`
- unauthenticated triggering of the locally configured `agents.yaml` workflow through `/chat`
- repeated consumption of model/API quota and any other side effects performed by that workflow
- exposure of whatever result `PraisonAI.run()` returns to the unauthenticated caller

This is not the same as arbitrary prompt injection by itself, because the current `/chat` handler ignores the submitted `message` value and simply runs the configured workflow. The impact therefore depends on what the operator's `agents.yaml` is allowed to do, but the authentication bypass is unconditional in the shipped legacy server.

## References
- https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-6rmh-7xcm-cpxj
- https://nvd.nist.gov/vuln/detail/CVE-2026-44338
- https://github.com/MervinPraison/PraisonAI
