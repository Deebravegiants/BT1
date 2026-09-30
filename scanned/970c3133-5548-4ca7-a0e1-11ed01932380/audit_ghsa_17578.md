# [M] Couchbase .NET SDK (client library) does not properly enable hostname verification for TLS certificates

## Summary
Severity: Medium
Advisory: GHSA-px2c-r924-mwcc
CVE: CVE-2025-49015
CWE: CWE-297
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-06-18
Source: https://github.com/advisories/GHSA-px2c-r924-mwcc
Type: github-advisory

## Affected
- NuGet: `CouchbaseNetClient` — affected >=0

## Details
The Couchbase .NET SDK (client library) before 3.7.1 does not properly enable hostname verification for TLS certificates. In fact, the SDK was also using IP addresses instead of hostnames due to a configuration option that was incorrectly enabled by default.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-49015
- https://github.com/couchbase/couchbase-net-client/commit/04d1679b2178f922036be6e595b3d91f972c5ba3
- https://docs.couchbase.com/server/current/release-notes/relnotes.html
- https://forums.couchbase.com/tags/security
- https://github.com/couchbase/couchbase-net-client
- https://www.couchbase.com/alerts
