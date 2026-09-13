# [M] OpenSearch Security plugin: DLS not applied on documents linked by has_child or has_parent relation

## Summary
Severity: Medium
Advisory: GHSA-x83w-23jp-g6pw
CWE: CWE-863
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-07
Source: https://github.com/advisories/GHSA-x83w-23jp-g6pw
Type: github-advisory

## Affected
- Maven: `org.opensearch.plugin:opensearch-security` — affected >=1.0.0 <2.19.4.0
- Maven: `org.opensearch.plugin:opensearch-security` — affected >=3.0.0 <3.2.0.0

## Details
### Description

A flaw was identified in the OpenSearch Security plugin's document-level security (DLS) implementation. DLS restrictions were not correctly applied to search queries that use has_parent or has_child join relations. This could allow an authenticated user to access document contents that should have been restricted by DLS rules.

### Impact

An authenticated user with access to an index containing parent/child join relations could bypass DLS restrictions on documents linked by those relations, potentially accessing restricted document contents. This only affects clusters that use both DLS and the `join` field type on the same index.

### Patches

 This issue is fixed in OpenSearch `2.19.4` and `3.2.0`.

### Workarounds

Avoid using the `join` field type on indices that are subject to DLS rules.

## References
- https://github.com/opensearch-project/security/security/advisories/GHSA-x83w-23jp-g6pw
- https://github.com/opensearch-project/security
