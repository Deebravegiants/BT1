# [C] SQL Injection in Couchbase Sync Gateway

## Summary
Severity: Critical
Advisory: GHSA-g622-r636-qfqh
CVE: CVE-2019-9039
CWE: CWE-89
Ecosystem: Go
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-02-15
Source: https://github.com/advisories/GHSA-g622-r636-qfqh
Type: github-advisory

## Affected
- Go: `github.com/couchbase/sync_gateway` — affected >=0 <2.5.0

## Details
The Couchbase Sync Gateway 2.1.2 in combination with a Couchbase Server is affected by a previously undisclosed N1QL-injection vulnerability in the REST API. An attacker with access to the public REST API can insert additional N1QL statements through the parameters ?startkey? and ?endkey? of the ?_all_docs? endpoint.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-9039
- https://github.com/couchbase/sync_gateway/commit/97adb5b496aa96aa70398018ea96da913ffd8d8c
- https://docs.couchbase.com/sync-gateway/2.5/release-notes.html
- https://research.hisolutions.com/2019/06/n1ql-injection-in-couchbase-sync-gateway-cve-2019-9039
- https://www.couchbase.com/resources/security#SecurityAlerts
