# [M] pgAdmin 4 Path Traversal vulnerability

## Summary
Severity: Medium
Advisory: GHSA-cr8c-972v-rmp3
CVE: CVE-2022-0959
CWE: CWE-22, CWE-434
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-03-17
Source: https://github.com/advisories/GHSA-cr8c-972v-rmp3
Type: github-advisory

## Affected
- PyPI: `pgadmin4` — affected >=0 <6.7

## Details
When run in server mode, pgAdmin 4 allows users to store files on the server under individual storage directories. Files such as SQL scripts may be uploaded through the user interface. The URI to which upload requests are made fails to validate the upload path to prevent path traversal techniques being used to store files outside of the storage directory. A malicious, but authorised and authenticated user can construct an HTTP request using their existing CSRF token and session cookie to manually upload files to any location that the operating system user account under which pgAdmin is running has permission to write.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-0959
- https://github.com/pgadmin-org/pgadmin4/commit/dccd4f0bbaafa783d9f0360c7592b128d5cc3928
- https://bugzilla.redhat.com/show_bug.cgi?id=2063759
- https://github.com/pgadmin-org/pgadmin4
