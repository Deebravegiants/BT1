# [H] LiteLLM has a sandbox escape in custom-code guardrail

## Summary
Severity: High
Advisory: GHSA-wxxx-gvqv-xp7p
CVE: CVE-2026-40217
CWE: CWE-420, CWE-913
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-11
Source: https://github.com/advisories/GHSA-wxxx-gvqv-xp7p
Type: github-advisory

## Affected
- PyPI: `litellm` — affected >=1.81.8 <1.83.10

## Details
### Impact

The `POST /guardrails/test_custom_code` endpoint runs user-supplied Python inside a hand-rolled sandbox. The sandbox can be escaped using bytecode-level techniques, allowing arbitrary code execution in the proxy process — which runs as root in the default Docker image.

**Reaching the endpoint requires a proxy-admin credential** in default configurations.

### Patches

Fixed in **`1.83.11`**. The hand-rolled sandbox has been replaced with `RestrictedPython`. Upgrade to `1.83.11` or later.

### Workarounds

If upgrading is not immediately possible, block `POST /guardrails/test_custom_code` at your reverse proxy or API gateway.

### References

- Patched release: [`v1.83.10-stable`](https://github.com/BerriAI/litellm/releases/tag/v1.83.10-stable)

## References
- https://github.com/BerriAI/litellm/security/advisories/GHSA-wxxx-gvqv-xp7p
- https://nvd.nist.gov/vuln/detail/CVE-2026-40217
- https://github.com/BerriAI/litellm
- https://github.com/BerriAI/litellm/releases/tag/v1.83.10-stable
- https://www.x41-dsec.de/lab/advisories/x41-2026-001-litellm
