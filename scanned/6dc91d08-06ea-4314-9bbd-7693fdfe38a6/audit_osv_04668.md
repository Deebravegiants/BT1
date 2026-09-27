# [M] Elasticsearch Incorrect Authorization in the Remote Cluster Security API key based security model

## Summary
Severity: Medium
Advisory: BIT-elasticsearch-2024-23451
Aliases: CVE-2024-23451, GHSA-r3hx-qfh5-r9m7
Ecosystem: Bitnami
Published: 2024-05-14
Source: https://osv.dev/vulnerability/BIT-elasticsearch-2024-23451
Type: osv

## Affected
- Bitnami: `elasticsearch` — affected >=8.10.0 <8.13.0

## Details
Incorrect Authorization issue exists in the API key based security model for Remote Cluster Security, which is currently in Beta, in Elasticsearch 8.10.0 and before 8.13.0. This allows a malicious user with a valid API key for a remote cluster configured to use the new Remote Cluster Security to read arbitrary documents from any index on the remote cluster, and only if they use the Elasticsearch custom transport protocol to issue requests with the target index ID, the shard ID and the document ID. None of Elasticsearch REST API endpoints are affected by this issue.

## References
- https://discuss.elastic.co/t/elasticsearch-8-13-0-security-update-esa-2024-07/356315
- https://nvd.nist.gov/vuln/detail/CVE-2024-23451
