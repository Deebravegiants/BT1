# [M] Missing Authorization in Kibana Leading to Unauthorized Elasticsearch Index Data Exposure

## Summary
Severity: Medium
Advisory: CVE-2026-78601
CVSS: 5.5 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:L/A:N)
Published: 2026-09-02
Source: https://osv.dev/vulnerability/CVE-2026-78601
Type: osv

## Details
Missing Authorization (CWE-862) in Kibana can lead to information disclosure via Privilege Abuse (CAPEC-122). An authorization control was not applied to a Kibana Entity Store configuration operation, allowing an authenticated user with elevated Kibana privileges to indirectly cause a background task to read from Elasticsearch indices that user is not authorized to access. Derived entity data from those indices is then exposed through the entity store output.

## References
- https://discuss.elastic.co/t/kibana-9-4-5-security-update-esa-2026-147/390107
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/78xxx/CVE-2026-78601.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-78601
