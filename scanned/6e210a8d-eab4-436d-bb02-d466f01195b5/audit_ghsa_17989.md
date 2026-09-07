# [M] OpenSearch unauthorized data access on fields protected by field level security if field is a member of an object

## Summary
Severity: Medium
Advisory: GHSA-2rjv-cv85-xhgm
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-08-01
Source: https://github.com/advisories/GHSA-2rjv-cv85-xhgm
Type: github-advisory

## Affected
- Maven: `org.opensearch.plugin:opensearch-security` — affected >=0 <2.19.3.0

## Details
### Impact

OpenSearch versions 2.19.2 and earlier improperly apply Field Level Security (FLS) rules on fields which are not at the top level of the source document tree (i.e., which are members of a JSON object). 

If an FLS exclusion rule (like `~object`) is applied to an object valued attribute in a source document, the object is properly removed from the `_source` document in search and get results. However, any member attribute of that object remains available to search queries. This allows to reconstruct the original field contents using range queries. 

### Patches

The issue has been resolved in OpenSearch 3.0.0 and OpenSearch 2.19.3.

### Workarounds

If FLS exclusion rules are used for object valued attributes  (like `~object`), add an additional exclusion rule for the members of the object  (like `~object.*`).

## References
- https://github.com/opensearch-project/security/security/advisories/GHSA-2rjv-cv85-xhgm
- https://github.com/opensearch-project/security
