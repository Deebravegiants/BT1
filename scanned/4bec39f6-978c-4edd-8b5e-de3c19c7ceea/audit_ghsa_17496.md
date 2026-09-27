# [M] Elasticsearch has Excessive Allocation of Resources via Submission of Oversized User Settings Data

## Summary
Severity: Medium
Advisory: GHSA-qf7c-7r9h-mm92
CVE: CVE-2025-68384
CWE: CWE-770
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-12-19
Source: https://github.com/advisories/GHSA-qf7c-7r9h-mm92
Type: github-advisory

## Affected
- Maven: `org.elasticsearch.plugin:x-pack-security` — affected >=0 <8.19.9
- Maven: `org.elasticsearch.plugin:x-pack-security` — affected >=9.0.0 <9.1.9
- Maven: `org.elasticsearch.plugin:x-pack-security` — affected >=9.2.0 <9.2.3

## Details
Allocation of Resources Without Limits or Throttling (CWE-770) in Elasticsearch can allow a low-privileged authenticated user to cause Excessive Allocation (CAPEC-130) causing a persistent denial of service (OOM crash) via submission of oversized user settings data.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-68384
- https://github.com/elastic/elasticsearch/pull/138691
- https://github.com/elastic/elasticsearch/commit/ab1d99ae033f2a23a8856b47a2d86652ad63a39a
- https://github.com/elastic/elasticsearch/commit/b46a4f64baea79c4d3afd58bda39d258de97210a
- https://discuss.elastic.co/t/elasticsearch-8-19-9-9-1-9-and-9-2-3-security-update-esa-2025-33/384181
- https://github.com/elastic/elasticsearch
