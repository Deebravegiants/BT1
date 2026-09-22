# [H] LiteLLM: Privilege escalation via unrestricted proxy configuration endpoint

## Summary
Severity: High
Advisory: GHSA-53mr-6c8q-9789
CVE: CVE-2026-35029
CWE: CWE-863
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2026-04-03
Source: https://github.com/advisories/GHSA-53mr-6c8q-9789
Type: github-advisory

## Affected
- PyPI: `litellm` — affected >=0 <1.83.0

## Details
### Impact

The `/config/update endpoint` does not enforce admin role authorization. A user who is already authenticated into the platform can then use this endpoint to do the following:

  - Modify proxy configuration and environment variables
  - Register custom pass-through endpoint handlers pointing to attacker-controlled Python code, achieving remote code execution
  - Read arbitrary server files by setting UI_LOGO_PATH and fetching via /get_image
  - Take over other priveleged accounts by overwriting UI_USERNAME and UI_PASSWORD environment variables

### Patches

Fixed in v1.83.0. The endpoint now requires `proxy_admin` role.

### Workarounds

Restrict API key distribution. There is no configuration-level workaround.

## References
- https://github.com/BerriAI/litellm/security/advisories/GHSA-53mr-6c8q-9789
- https://nvd.nist.gov/vuln/detail/CVE-2026-35029
- https://github.com/BerriAI/litellm
- http://seclists.org/fulldisclosure/2026/Apr/17
