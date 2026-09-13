# [M] pgAdmin failed to properly control the server code 

## Summary
Severity: Medium
Advisory: GHSA-ghp8-52vx-77j4
CVE: CVE-2023-5002
CWE: CWE-78
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:R/S:U/C:L/I:H/A:H (CVSS_V3)
Published: 2023-09-22
Source: https://github.com/advisories/GHSA-ghp8-52vx-77j4
Type: github-advisory

## Affected
- PyPI: `pgadmin4` — affected >=0 <7.7

## Details
A flaw was found in pgAdmin. This issue occurs when the pgAdmin server HTTP API validates the path a user selects to external PostgreSQL utilities such as pg_dump and pg_restore. Versions of pgAdmin prior to 7.7 failed to properly control the server code executed on this API, allowing an authenticated user to run arbitrary commands on the server.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-5002
- https://github.com/pgadmin-org/pgadmin4/issues/6763
- https://github.com/pgadmin-org/pgadmin4/commit/35f05e49b3632a0a674b9b36535a7fe2d93dd0c2
- https://bugzilla.redhat.com/show_bug.cgi?id=2239164
- https://github.com/pgadmin-org/pgadmin4
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/2S24D3S2GVNGTDNE6SF2OQSOPU3H72UW
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/VIRTMQZEE6K7RD37ERZ2UFYFLEUXLQU3
