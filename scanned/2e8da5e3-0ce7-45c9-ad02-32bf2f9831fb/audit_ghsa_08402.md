# [H] IKUS Rdiffweb allows an attacker with any valid or stolen access token to act as other users

## Summary
Severity: High
Advisory: GHSA-v4gp-hf5j-4566
CVE: CVE-2025-67796
CWE: CWE-284
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-05-04
Source: https://github.com/advisories/GHSA-v4gp-hf5j-4566
Type: github-advisory

## Affected
- PyPI: `rdiffweb` — affected >=0 <2.10.6

## Details
IKUS Rdiffweb version 2.10.5 and below have an improper authorization flaw that allows an attacker with any valid or stolen access token to act as other users. The API does not enforce binding between the authenticated subject and the targeted user/tenant, so crafted requests can read or modify other users data and, in some cases, perform privileged actions. This issue may enable cross-tenant access. Fixed in version 2.10.6.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-67796
- https://gitlab.com/ikus-soft/rdiffweb
- https://gitlab.com/ikus-soft/rdiffweb#2106-2025-10-02
