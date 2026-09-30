# [M] OpenSearch unauthorized data access on fields protected by field masking for fields of type ip, geo_point, geo_shape, xy_point, xy_shape

## Summary
Severity: Medium
Advisory: GHSA-rrmm-wq7q-h4v5
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-08-01
Source: https://github.com/advisories/GHSA-rrmm-wq7q-h4v5
Type: github-advisory

## Affected
- Maven: `org.opensearch.plugin:opensearch-security` — affected >=0 <2.19.3.0

## Details
### Impact

OpenSearch versions 2.19.2 and earlier improperly apply field masking rules on fields of the types `ip`, `geo_point`, `geo_shape`, `xy_point`, `xy_shape`. While the content of these fields is properly redacted in the `_source` document returned by search operations, the original unredacted values remain available to search queries. This allows to reconstruct the original field contents using range queries.

Additionally, the content of fields of type `geo_point`, `geo_shape`, `xy_point`, `xy_shape` is returned in an unredacted form if requested via the `fields` option of the search API.

### Patches

The issue has been resolved in OpenSearch 3.0.0 and OpenSearch 2.19.3.

### Workarounds

If you cannot upgrade immediately, you can avoid the problem by using field level security (FLS) protection on fields of the affected types instead of field masking.

## References
- https://github.com/opensearch-project/security/security/advisories/GHSA-rrmm-wq7q-h4v5
- https://github.com/opensearch-project/security
