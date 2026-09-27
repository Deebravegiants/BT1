# [H] CVE-2024-56528

## Summary
Severity: High
Advisory: CVE-2024-56528
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-04-03
Source: https://osv.dev/vulnerability/CVE-2024-56528
Type: osv

## Details
This vulnerability affects Snowplow Collector 3.x before 3.3.0 (unless it’s set up behind a reverse proxy that establishes payload limits). It involves sending very large payloads to the Collector and can render it unresponsive to the rest of the requests. As a result, data would not enter the pipeline and would be potentially lost.

## References
- https://support.snowplow.io/hc/en-us/articles/26318139354909-Update-Critical-Snowplow-Security-Updates-Impact-on-Open-Source-Software-Users
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56528.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56528
