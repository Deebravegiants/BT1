# [M] Elastic Agent Insertion of Sensitive Information into Log File

## Summary
Severity: Medium
Advisory: CVE-2023-6687
CVSS: 6.8 (CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N)
Published: 2023-12-12
Source: https://osv.dev/vulnerability/CVE-2023-6687
Type: osv

## Details
An issue was discovered by Elastic whereby Elastic Agent would log a raw event in its own logs at the WARN or ERROR level if ingesting that event to Elasticsearch failed with any 4xx HTTP status code except 409 or 429. Depending on the nature of the event that Elastic Agent attempted to ingest, this could lead to the insertion of sensitive or private information in the Elastic Agent logs. Elastic has released 8.11.3 and 7.17.16 that prevents this issue by limiting these types of logs to DEBUG level logging, which is disabled by default.

## References
- https://discuss.elastic.co/t/beats-and-elastic-agent-8-11-3-7-17-16-security-update-esa-2023-30/349180
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/6xxx/CVE-2023-6687.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-6687
