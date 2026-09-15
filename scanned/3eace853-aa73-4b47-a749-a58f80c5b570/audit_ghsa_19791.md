# [H] LiteLLM Has an Improper Authorization Vulnerability

## Summary
Severity: High
Advisory: GHSA-fjcf-3j3r-78rp
CVE: CVE-2025-0628
CWE: CWE-266, CWE-285
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2025-03-20
Source: https://github.com/advisories/GHSA-fjcf-3j3r-78rp
Type: github-advisory

## Affected
- PyPI: `litellm` — affected >=0 <1.61.15

## Details
An improper authorization vulnerability exists in the main-latest version of BerriAI/litellm. When a user with the role 'internal_user_viewer' logs into the application, they are provided with an overly privileged API key. This key can be used to access all the admin functionality of the application, including endpoints such as '/users/list' and '/users/get_users'. This vulnerability allows for privilege escalation within the application, enabling any account to become a PROXY ADMIN.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-0628
- https://github.com/berriai/litellm/commit/566d9354aab4215091b2e51ad0333e948125fa1b
- https://github.com/BerriAI/litellm
- https://huntr.com/bounties/6c0e2f75-2d03-42f9-9530-e16a973317fc
