# [H] pgAdmin has Incorrect Default Permissions

## Summary
Severity: High
Advisory: GHSA-7w6r-748w-mh52
CVE: CVE-2023-1907
CWE: CWE-276, CWE-488
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2025-01-09
Source: https://github.com/advisories/GHSA-7w6r-748w-mh52
Type: github-advisory

## Affected
- PyPI: `pgadmin4` — affected >=0 <7.0

## Details
A vulnerability was found in pgadmin. Users logging into pgAdmin running in server mode using LDAP authentication may be attached to another user's session if multiple connection attempts occur simultaneously.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-1907
- https://github.com/pgadmin-org/pgadmin4/issues/6100
- https://github.com/pgadmin-org/pgadmin4/commit/fa29ba91632634d961f937ce3ed2c3b5a9d78f59
- https://access.redhat.com/security/cve/CVE-2023-1907
- https://bugzilla.redhat.com/show_bug.cgi?id=2218384
- https://github.com/pgadmin-org/pgadmin4
- https://github.com/pgadmin-org/pgadmin4/blob/a9974b418c49760d3989b7fb25e052ff16b89ac6/docs/en_US/release_notes_7_0.rst
