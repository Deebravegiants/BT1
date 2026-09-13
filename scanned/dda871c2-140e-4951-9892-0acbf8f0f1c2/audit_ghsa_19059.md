# [H] pgAdmin has vulnerability in LDAP authentication mechanism that allows bypassing TLS certificate verification

## Summary
Severity: High
Advisory: GHSA-g4r8-3qmh-pmch
CVE: CVE-2025-12765
CWE: CWE-295
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-11-13
Source: https://github.com/advisories/GHSA-g4r8-3qmh-pmch
Type: github-advisory

## Affected
- PyPI: `pgadmin4` — affected >=0 <9.10

## Details
pgAdmin <= 9.9 is affected by a vulnerability in the LDAP authentication mechanism allows bypassing TLS certificate verification.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-12765
- https://github.com/pgadmin-org/pgadmin4/issues/9324
- https://github.com/pgadmin-org/pgadmin4/commit/09d2b7eeb0e330df73b1aef0cba57788fde52b6b
- https://github.com/pgadmin-org/pgadmin4
