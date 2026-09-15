# [M] CrateDB's Blob HTTP handler bypasses authorization

## Summary
Severity: Medium
Advisory: CVE-2026-49989
Aliases: GHSA-2xv8-gjwh-fv8p
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-14
Source: https://osv.dev/vulnerability/CVE-2026-49989
Type: osv

## Details
CrateDB is a distributed SQL database. Prior to versions 6.2.8 and 6.3.2, any authenticated user can read or delete any blob whose SHA-1 digest they know, and can plant new blobs unconditionally, in any blob table, regardless of `GRANT`s. CrateDB has two ways to access blob storage: SQL (`SELECT ... FROM blob.<table>` and friends) and the blob HTTP API (`GET|PUT|DELETE /_blobs/{table}/{digest}`). The SQL path goes through `AccessControl`, which is what enforces privilege grants; that's why `SELECT digest FROM blob.secret_blobs` fails for a user who has no grants on the table. The HTTP path authenticates the request but never asks `AccessControl` whether the authenticated user is allowed to touch the table. So a user with no grants gets `MissingPrivilegeException` from SQL and `200 OK` plus the blob bytes from `GET /_blobs/secret_blobs/<digest>`. Deployments that don't use `BLOB TABLE` are unaffected. Authentication itself still works; the bug is strictly that being authenticated as anyone is treated as sufficient for any blob op. Versions 6.2.8 and 6.3.2 fix the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/49xxx/CVE-2026-49989.json
- https://github.com/crate/crate/security/advisories/GHSA-2xv8-gjwh-fv8p
- https://nvd.nist.gov/vuln/detail/CVE-2026-49989
