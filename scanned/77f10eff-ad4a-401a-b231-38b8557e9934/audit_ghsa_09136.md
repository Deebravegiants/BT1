# [C] PraisonAI `deploy --type api` emits a Flask server with authentication disabled by default

## Summary
Severity: Critical
Advisory: GHSA-8444-4fhq-fxpq
CVE: CVE-2026-47393
CWE: CWE-1188, CWE-306
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-29
Source: https://github.com/advisories/GHSA-8444-4fhq-fxpq
Type: github-advisory

## Affected
- PyPI: `PraisonAI` — affected >=0 <4.6.40

## Details
### Summary

CVE-2026-44338 (GHSA-6rmh-7xcm-cpxj) documents that PraisonAI ships a code-generator (`praisonai.deploy.api.generate_api_server_code`) that emits a Flask API server with authentication disabled by default. Users who follow the documented quickstart (`praisonai deploy --type api`) get a server that:

- binds to `0.0.0.0` per the recommended sample YAML
- exposes `/chat` and `/agents` endpoints
- runs `praisonai.run()` on user-supplied JSON input — LLM orchestration with the API key materials present in the process environment
- does not require any authentication

The PyPI wheel `praisonai==4.6.33` (current `@latest`) still ships the generator with `auth_enabled` defaulting to `False`. The fix shape is opt-in via `APIConfig(auth_enabled=True, auth_token=...)`.

### Details

**Anchor (file:line:symbol)**

- Vulnerable artifact: `praisonai==4.6.33` on PyPI.
- Defaults: `praisonai/deploy/models.py:29` — `auth_enabled: bool = Field(default=False, ...)`; `praisonai/deploy/models.py:30` — `auth_token: Optional[str] = Field(default=None, ...)`.
- Generator: `praisonai/deploy/api.py:40` — `AUTH_ENABLED = {config.auth_enabled}`; `api.py:41` — `AUTH_TOKEN = {repr(config.auth_token)}`; `api.py:43-49` — `def check_auth(): if not AUTH_ENABLED: return True`.
- CLI entry: documented as `praisonai deploy --type api` (vendor README); produces the generator output above with no flag required to suppress the warning, because no warning is emitted.

**Vulnerable code (verbatim from installed wheel)**

```python
# praisonai/deploy/models.py (praisonai==4.6.33)
class APIConfig(BaseModel):
    host: str = Field(default="127.0.0.1", description="Server host")
    port: int = Field(default=8005, description="Server port")
    cors_enabled: bool = Field(default=True, description="Enable CORS")
    auth_enabled: bool = Field(default=False, description="Enable authentication")     # line 29
    auth_token: Optional[str] = Field(default=None, description="Authentication token") # line 30
```

```python
# praisonai/deploy/api.py (praisonai==4.6.33)
code = f\'\'\'...
# Authentication
AUTH_ENABLED = {config.auth_enabled}      # False by default
AUTH_TOKEN   = {repr(config.auth_token)}  # None by default

def check_auth():
    if not AUTH_ENABLED:
        return True                       # short-circuit, accept all
    token = request.headers.get(\'Authorization\', \'\').replace(\'Bearer \', \'\')
    return token == AUTH_TOKEN
...
\'\'\'
```

A default invocation of the deploy command emits a server whose `check_auth()` short-circuits to `True` and accepts unauthenticated `/chat`, `/agents` POSTs.

### PoC

```python
#!/usr/bin/env python3
"""
legend-c420 PoC - PraisonAI 4.6.33 generates Flask API server with auth
disabled by default. Class H sibling of CVE-2026-44338.

Phase 1: reflect on praisonai.deploy.models.APIConfig defaults.
Phase 2: call generate_api_server_code(default config) and assert the
         emitted source contains AUTH_ENABLED = False and the
         short-circuit return.
Phase 3: re-run with auth_enabled=True, auth_token='s3cret-bearer-value'
         and confirm the emitted source flips to the secure shape.

Exit code 0 = PASS = vulnerable defaults confirmed.
"""
import sys, traceback

def phase1_dataclass_defaults():
    print("PHASE 1 - praisonai.deploy.models.APIConfig default values")
    from praisonai.deploy.models import APIConfig
    cfg = APIConfig()
    checks = [
        ("auth_enabled", cfg.auth_enabled, False),
        ("auth_token",   cfg.auth_token,   None),
    ]
    for name, observed, expected in checks:
        ok = observed == expected
        mark = "VULNERABLE" if name in ("auth_enabled","auth_token") and ok else "ok"
        print(f"  {name:14s} = {observed!r:18s}  (expected {expected!r})  [{mark}]")
        assert ok
    print("  >> APIConfig defaults reproduce the CVE-2026-44338 shape.")

def phase2_default_generator_emits_unauth():
    print("PHASE 2 - generate_api_server_code(default config) emits unauth server")
    from praisonai.deploy.models import APIConfig
    from praisonai.deploy.api import generate_api_server_code
    src = generate_api_server_code("agents.yaml", config=APIConfig())
    for needle in ["AUTH_ENABLED = False","AUTH_TOKEN = None","if not AUTH_ENABLED:","return True"]:
        assert needle in src, f"missing: {needle!r}"
        print(f"  [FOUND] {needle!r}")
    print("  >> Default-config generator emits Flask server with check_auth() short-circuit.")

def phase3_fix_shape_available():
    print("PHASE 3 - auth_enabled=True flips to secure shape")
    from praisonai.deploy.models import APIConfig
    from praisonai.deploy.api import generate_api_server_code
    cfg = APIConfig(auth_enabled=True, auth_token="s3cret-bearer-value")
    src = generate_api_server_code("agents.yaml", config=cfg)
    assert "AUTH_ENABLED = True" in src
    assert "AUTH_ENABLED = False" not in src
    print("  >> Fix shape works when toggled. Class H confirmed: default is insecure.")

def main():
    print("=" * 64)
    print("legend-c420 PoC - PraisonAI default-config AUTH_ENABLED=False")
    print("=" * 64)
    try:
        phase1_dataclass_defaults()
        phase2_default_generator_emits_unauth()
        phase3_fix_shape_available()
    except Exception:
        traceback.print_exc()
        print("FAIL"); sys.exit(2)
    print("PASS 3/3 phases. EXIT 0.")
    sys.exit(0)

if __name__ == "__main__":
    main()
```

**PoC dependencies:** `praisonai==4.6.33` from PyPI. Tested on Python 3.11.

**Run log verdict:** `PASS 3/3 phases. EXIT 0.` — vulnerable-default shape confirmed. `auth_enabled=False` by default, `check_auth()` short-circuits to `True`, fix toggle exists but is opt-in.

### Impact

An operator who runs the vendor-documented quickstart (`pip install praisonai && praisonai deploy --type api`) gets a network-reachable Flask server that invokes `praisonai.run()` on attacker-supplied JSON with the user's LLM API keys in the process environment. The attacker reaches arbitrary LLM-orchestration (including any tool-use the agents define, which in PraisonAI commonly includes `python_repl`, `bash`, file I/O, and HTTP calls), with the host's API-key credit billed to the operator.

- **Belief:** CVE-2026-44338 was filed and triaged.
- **Reality:** `praisonai==4.6.33` is current `@latest` on PyPI (2026-05-16). The generator still defaults to `auth_enabled=False`.
- **Gap:** The CVE acknowledges the fix shape exists. The fix is opt-in. The default-config consumer remains vulnerable.

**Parent CVE:** CVE-2026-44338 / GHSA-6rmh-7xcm-cpxj

## References
- https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-8444-4fhq-fxpq
- https://github.com/MervinPraison/PraisonAI
- https://github.com/advisories/GHSA-6rmh-7xcm-cpxj
