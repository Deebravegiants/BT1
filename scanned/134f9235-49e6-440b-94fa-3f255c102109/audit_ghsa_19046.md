# [H] pgAdmin is affected by an LDAP injection vulnerability

## Summary
Severity: High
Advisory: GHSA-cvf4-f829-762v
CVE: CVE-2025-12764
CWE: CWE-90
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-11-13
Source: https://github.com/advisories/GHSA-cvf4-f829-762v
Type: github-advisory

## Affected
- PyPI: `pgadmin4` — affected >=0 <9.10

## Details
pgAdmin <= 9.9 is affected by an LDAP injection vulnerability in the LDAP authentication flow that allows an attacker to inject special LDAP characters in the username, causing the DC/LDAP server and the client to process an unusual amount of data DOS.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-12764
- https://github.com/pgadmin-org/pgadmin4/issues/9325
- https://github.com/pgadmin-org/pgadmin4/commit/09d2b7eeb0e330df73b1aef0cba57788fde52b6b
- https://github.com/pgadmin-org/pgadmin4
