# [H] Couchbase Sync Gateway shows cleartext passwords in redacted and unredacted output

## Summary
Severity: High
Advisory: GHSA-pqhp-4xfc-hjgq
CVE: CVE-2025-52490
CWE: CWE-319
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2025-07-29
Source: https://github.com/advisories/GHSA-pqhp-4xfc-hjgq
Type: github-advisory

## Affected
- Go: `github.com/couchbase/sync_gateway` — affected >=0 <3.2.6

## Details
An issue was discovered in Couchbase Sync Gateway before 3.2.6. In sgcollect_info_options.log and sync_gateway.log, there are cleartext passwords in redacted and unredacted output.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-52490
- https://docs.couchbase.com/server/current/release-notes/relnotes.html
- https://forums.couchbase.com/tags/security
- https://github.com/couchbase/sync_gateway
- https://www.couchbase.com/alerts
