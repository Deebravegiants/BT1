# [M] Incorrect Error Handling Allowed Partial File Reads Over REST API in OpenSearch

## Summary
Severity: Medium
Advisory: CVE-2022-41917
Aliases: GHSA-w3rx-m34v-wrqx
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2022-11-15
Source: https://osv.dev/vulnerability/CVE-2022-41917
Type: osv

## Details
OpenSearch is a community-driven, open source fork of Elasticsearch and Kibana. OpenSearch allows users to specify a local file when defining text analyzers to process data for text analysis. An issue in the implementation of this feature allows certain specially crafted queries to return a response containing the first line of text from arbitrary files. The list of potentially impacted files is limited to text files with read permissions allowed in the Java Security Manager policy configuration. OpenSearch version 1.3.7 and 2.4.0 contain a fix for this issue. Users are advised to upgrade. There are no known workarounds for this issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/41xxx/CVE-2022-41917.json
- https://github.com/opensearch-project/OpenSearch/security/advisories/GHSA-w3rx-m34v-wrqx
- https://nvd.nist.gov/vuln/detail/CVE-2022-41917
- https://github.com/opensearch-project/OpenSearch/commit/6d20423f5920745463b1abc5f1daf6a786c41aa0
