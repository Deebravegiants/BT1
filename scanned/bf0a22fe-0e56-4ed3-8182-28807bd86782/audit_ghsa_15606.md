# [H] OAuth2 client ID and secret exposed through the web browser

## Summary
Severity: High
Advisory: GHSA-jm9x-rx9x-wpqj
CVE: CVE-2024-9014
CWE: CWE-522
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2024-09-23
Source: https://github.com/advisories/GHSA-jm9x-rx9x-wpqj
Type: github-advisory

## Affected
- PyPI: `pgadmin4` — affected >=0 <8.12

## Details
pgAdmin versions 8.11 and earlier are vulnerable to a security flaw in OAuth2 authentication. This vulnerability allows an attacker to potentially obtain the client ID and secret, leading to unauthorized access to user data.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-9014
- https://github.com/pgadmin-org/pgadmin4/issues/7945
- https://github.com/pgadmin-org/pgadmin4
- https://www.pgadmin.org/docs/pgadmin4/8.12/release_notes_8_12.html
