# [M] Memory Allocation with Excessive Size Value in Elasticsearch Leading to Denial of Service

## Summary
Severity: Medium
Advisory: CVE-2026-72645
Aliases: BIT-elasticsearch-2026-72645
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/CVE-2026-72645
Type: osv

## Details
Memory Allocation with Excessive Size Value (CWE-789) in Elasticsearch can lead to denial of service via Excessive Allocation (CAPEC-130). An authenticated user holding only read privileges on a single index can submit one small, specially crafted search request that causes an excessively large memory allocation, exhausting the JVM heap and terminating the affected node.

## References
- https://discuss.elastic.co/t/elasticsearch-8-19-20-9-4-5-9-5-1-security-update-esa-2026-116/389502
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72645.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72645
