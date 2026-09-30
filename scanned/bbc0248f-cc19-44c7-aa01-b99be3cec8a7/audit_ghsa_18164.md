# [H] pgadmin4 is affected by a Cross-Origin Opener Policy (COOP) vulnerability

## Summary
Severity: High
Advisory: GHSA-6859-2qxq-ffv2
CVE: CVE-2025-9636
CWE: CWE-346
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:C/C:H/I:H/A:L (CVSS_V3)
Published: 2025-09-05
Source: https://github.com/advisories/GHSA-6859-2qxq-ffv2
Type: github-advisory

## Affected
- PyPI: `pgadmin4` — affected >=0 <9.8

## Details
pgAdmin <= 9.7 is affected by a Cross-Origin Opener Policy (COOP) vulnerability. This vulnerability allows an attacker to manipulate the OAuth flow, potentially leading to unauthorised account access, account takeover, data breaches, and privilege escalation.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-9636
- https://github.com/pgadmin-org/pgadmin4/issues/9114
- https://github.com/pgadmin-org/pgadmin4/commit/cdeb18fcbb139a200b5a4779c82f9cd1aaaf3c89
- https://github.com/pgadmin-org/pgadmin4
