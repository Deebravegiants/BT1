# [M] Improper Handling of Highly Compressed Data in Kibana Leading to Denial of Service

## Summary
Severity: Medium
Advisory: CVE-2026-72628
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-09-01
Source: https://osv.dev/vulnerability/CVE-2026-72628
Type: osv

## Details
Improper Handling of Highly Compressed Data (CWE-409) in Kibana can lead to a denial of service via Excessive Allocation (CAPEC-130). An authenticated user holding Streams management privileges could supply specially crafted content that expands to a far larger volume of data during processing, exhausting the memory available to Kibana. The Kibana process is terminated by the host and remains unavailable to all users until the service is restarted.

## References
- https://discuss.elastic.co/t/kibana-8-19-21-9-4-6-9-5-2-security-update-esa-2026-125/390090
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72628.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72628
