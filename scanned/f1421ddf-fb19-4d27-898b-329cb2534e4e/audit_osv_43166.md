# [M] Uncontrolled Recursion in Elasticsearch Wildcard Matching Leading to Denial of Service

## Summary
Severity: Medium
Advisory: CVE-2026-72636
Aliases: BIT-elasticsearch-2026-72636
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/CVE-2026-72636
Type: osv

## Details
Uncontrolled Recursion (CWE-674) in the Elasticsearch wildcard matching helper can lead to a denial of service via Excessive Allocation (CAPEC-130). The matcher used to resolve wildcard patterns against names is implemented recursively and had no bound on recursion depth or on the total number of match operations performed. A search request containing a wildcard pattern with a large number of wildcard groups, evaluated against a sufficiently long name, exhausts the thread stack. Elasticsearch treats a stack overflow as an unrecoverable condition and shuts the node down, so the request terminates the affected node rather than failing gracefully.

## References
- https://discuss.elastic.co/t/elasticsearch-8-19-20-9-4-5-security-update-esa-2026-133/389499
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72636.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72636
