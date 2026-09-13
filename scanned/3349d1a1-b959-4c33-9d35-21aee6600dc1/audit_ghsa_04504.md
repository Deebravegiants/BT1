# [C] Crawl4AI: AST Sandbox Escape via gi_frame.f_back Chain - Pre-Auth RCE in Docker API

## Summary
Severity: Critical
Advisory: GHSA-qxjp-w3pj-48m7
CVE: CVE-2026-53753
CWE: CWE-913, CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-16
Source: https://github.com/advisories/GHSA-qxjp-w3pj-48m7
Type: github-advisory

## Affected
- PyPI: `crawl4ai` — affected >=0 <0.8.7

## Details
### Summary

The `_safe_eval_expression()` function in the computed fields feature uses an AST validator that only blocks attributes starting with underscore. Python generator and frame object attributes (`gi_frame`, `f_back`, `f_builtins`) do NOT start with underscore, enabling a complete sandbox escape to achieve arbitrary code execution.

The attack requires no authentication (JWT disabled by default) and is triggered via `POST /crawl` with a crafted extraction schema.

### Attack Vector

An attacker sends a `POST /crawl` request with a `JsonCssExtractionStrategy` schema containing a malicious computed field expression that:
1. Creates a generator to access `gi_frame`
2. Walks the frame chain via `f_back`
3. Reaches `f_builtins` containing the real `__import__`
4. Imports `os` and executes arbitrary commands

### Impact

Unauthenticated remote code execution inside the Docker container. An attacker can execute arbitrary system commands, read/write files, and exfiltrate secrets.

### Fix Details

1. Removed `eval()` from computed field expression path entirely -- expressions now log a warning and return default value
2. Deleted `_safe_eval_expression()` function and `_SAFE_EVAL_BUILTINS` (dead security-sensitive code)
3. `function` key with Python callables still works for SDK users
4. Replaced `eval()` in `/config/dump` with JSON-based input validated by Pydantic
5. Fixed hook_manager sandbox: stripped `__builtins__`, `__loader__`, `__spec__` from injected modules; removed `getattr`, `setattr`, `type`, `__build_class__` from allowed builtins

### Workarounds

1. Upgrade to the patched version (recommended)
2. Enable JWT authentication via `CRAWL4AI_API_TOKEN` environment variable
3. Restrict network access to the Docker API

### Credits

- Song Binglin ([q1uf3ng](https://github.com/q1uf3ng)) - reported the AST sandbox escape
- by111 ([August829](https://github.com/August829)) - reported the hook sandbox `__builtins__` escape and hardcoded JWT secret bypass
- [jannahopp](https://github.com/jannahopp) - PR #1855 proposing eval removal
- [ntohidi](https://github.com/ntohidi) - PR #1886 proposing allowlist approach

## References
- https://github.com/unclecode/crawl4ai/security/advisories/GHSA-qxjp-w3pj-48m7
- https://nvd.nist.gov/vuln/detail/CVE-2026-53753
- https://github.com/unclecode/crawl4ai/pull/1855
- https://github.com/unclecode/crawl4ai/pull/1886
- https://github.com/advisories/GHSA-qxjp-w3pj-48m7
- https://github.com/pypa/advisory-database/tree/main/vulns/crawl4ai/PYSEC-2026-319.yaml
- https://github.com/unclecode/crawl4ai
- https://pypi.org/project/crawl4ai
