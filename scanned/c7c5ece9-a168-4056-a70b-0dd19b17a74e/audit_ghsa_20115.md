# [H] pgadmin4 vulnerable to Code Injection

## Summary
Severity: High
Advisory: GHSA-3v6v-2x6p-32mc
CVE: CVE-2022-4223
CWE: CWE-862, CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-12-13
Source: https://github.com/advisories/GHSA-3v6v-2x6p-32mc
Type: github-advisory

## Affected
- PyPI: `pgadmin4` — affected >=0 <6.17

## Details
The pgAdmin server includes an HTTP API that is intended to be used to validate the path a user selects to external PostgreSQL utilities such as pg_dump and pg_restore. The utility is executed by the server to determine what PostgreSQL version it is from. Versions of pgAdmin prior to 6.17 failed to properly secure this API, which could allow an unauthenticated user to call it with a path of their choosing, such as a UNC path to a server they control on a Windows machine. This would cause an appropriately named executable in the target path to be executed by the pgAdmin server.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-4223
- https://github.com/pgadmin-org/pgadmin4/issues/5593
- https://github.com/pgadmin-org/pgadmin4
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/R5EYTPKHVFSDCETBJI7LBZE4EYHBPN2Q
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/R5EYTPKHVFSDCETBJI7LBZE4EYHBPN2Q
