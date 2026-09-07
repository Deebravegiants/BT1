# [H] GeoNetwork has ACL bypass on Elasticsearch search when request body omits query field

## Summary
Severity: High
Advisory: GHSA-582q-v28r-7cxr
CVE: CVE-2026-46487
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-07-01
Source: https://github.com/advisories/GHSA-582q-v28r-7cxr
Type: github-advisory

## Affected
- Maven: `org.geonetwork-opensource:geonetwork` — affected >=4.0.0-alpha.1
- Maven: `org.geonetwork-opensource:geonetwork` — affected >=4.2.0 <4.2.16
- Maven: `org.geonetwork-opensource:geonetwork` — affected >=4.4.0 <4.4.11

## Details
### Summary
GeoNetwork's Elasticsearch-backed search API is responsible for injecting access-control and visibility filters into every request before it reaches the underlying Elasticsearch index. Under certain request conditions, that filtering step does not run, allowing an unauthenticated user to retrieve indexed metadata records that should be restricted, including records limited to specific groups.

### Details
The search proxy layer forwards client-supplied search requests to Elasticsearch after adding GeoNetwork's own access-control and filter clauses. A flaw in how that filter-injection step is triggered means it can be skipped under certain conditions, so the affected request reaches Elasticsearch without the intended access restrictions applied.

### Impact
This is an authorization bypass leading to information disclosure (CWE-862: Missing Authorization). The skipped filter step is responsible for enforcing several layers of access control at once: group-based record visibility, draft record exclusion, record ownership checks, and portal-specific filtering.

Any public-facing GeoNetwork 4.x instance (4.0.0-alpha.1 through 4.4.10) is affected. An unauthenticated attacker can retrieve the full contents of metadata records that should not be publicly visible.

## References
- https://github.com/geonetwork/core-geonetwork/security/advisories/GHSA-582q-v28r-7cxr
- https://github.com/geonetwork/core-geonetwork
