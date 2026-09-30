# [M] Elastic Beats inserts sensitive information into log file

## Summary
Severity: Medium
Advisory: GHSA-hj4r-2c9c-29h3
CVE: CVE-2023-49922
CWE: CWE-532
Ecosystem: Go
CVSS: CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2023-12-12
Source: https://github.com/advisories/GHSA-hj4r-2c9c-29h3
Type: github-advisory

## Affected
- Go: `github.com/elastic/beats/v7` — affected >=7.0.0 <7.17.16
- Go: `github.com/elastic/beats` — affected >=8.0.0 <8.11.3
- Go: `github.com/elastic/beats` — affected >=7.0.0 <7.17.16

## Details
An issue was discovered by Elastic whereby Beats and Elastic Agent would log a raw event in its own logs at the WARN or ERROR level if ingesting that event to Elasticsearch failed with any 4xx HTTP status code except 409 or 429. Depending on the nature of the event that Beats or Elastic Agent attempted to ingest, this could lead to the insertion of sensitive or private information in the Beats or Elastic Agent logs. Elastic has released 8.11.3 and 7.17.16 that prevents this issue by limiting these types of logs to DEBUG level logging, which is disabled by default.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-49922
- https://github.com/elastic/beats/commit/9bd7de84ab9c31bb4e1c0a348a7b7c26817a0996
- https://discuss.elastic.co/t/beats-and-elastic-agent-8-11-3-7-17-16-security-update-esa-2023-30/349180
- https://github.com/elastic/beats
