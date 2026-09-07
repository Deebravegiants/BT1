# [M] Elasticsearch privileged authenticated users can cause DoS through Excessive Resource Allocation 

## Summary
Severity: Medium
Advisory: GHSA-gphj-4h6p-37xq
CVE: CVE-2025-68390
CWE: CWE-770
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-12-19
Source: https://github.com/advisories/GHSA-gphj-4h6p-37xq
Type: github-advisory

## Affected
- Maven: `org.elasticsearch.plugin:x-pack-core` — affected >=0 <8.19.8
- Maven: `org.elasticsearch.plugin:x-pack-core` — affected >=9.0.0 <9.1.8
- Maven: `org.elasticsearch.plugin:x-pack-core` — affected >=9.2.0 <9.2.2

## Details
Allocation of Resources Without Limits or Throttling (CWE-770) in Elasticsearch can allow an authenticated user with snapshot restore privileges to cause Excessive Allocation (CAPEC-130) of memory and a denial of service (DoS) via crafted HTTP request.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-68390
- https://github.com/elastic/elasticsearch/pull/138132
- https://discuss.elastic.co/t/elasticsearch-8-19-8-9-1-8-and-9-2-2-security-update-esa-2025-37/384185
- https://github.com/elastic/elasticsearch
