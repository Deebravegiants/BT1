# [C] misp-modules website - Missing CSRF protection in the website home blueprint

## Summary
Severity: Critical
Advisory: GHSA-j4rh-7jcr-qm69
CVE: CVE-2026-44364
CWE: CWE-352
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:P/VC:H/VI:H/VA:N/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2026-05-06
Source: https://github.com/advisories/GHSA-j4rh-7jcr-qm69
Type: github-advisory

## Affected
- PyPI: `misp-modules` — affected >=0

## Details
A Cross-Site Request Forgery vulnerability in the MISP Modules website allowed an attacker to cause an authenticated user to submit unintended requests to the home endpoint. The vulnerability was due to the home blueprint being exempted from CSRF protection. This could allow modification of session query data in the context of the authenticated user. The issue was fixed by enabling CSRF protection for the affected blueprint and hardening query parsing. As reported by Bilal Teke.

## References
- https://github.com/MISP/misp-modules/security/advisories/GHSA-j4rh-7jcr-qm69
- https://nvd.nist.gov/vuln/detail/CVE-2026-44364
- https://github.com/MISP/misp-modules/commit/52cda9caa003cafe87e14ae3721db5e16f6f111a
- https://github.com/MISP/misp-modules
