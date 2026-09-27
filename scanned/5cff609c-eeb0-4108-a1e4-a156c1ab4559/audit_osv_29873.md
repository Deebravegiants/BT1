# [M] CVE-2024-47217

## Summary
Severity: Medium
Advisory: CVE-2024-47217
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-04-03
Source: https://osv.dev/vulnerability/CVE-2024-47217
Type: osv

## Details
An issue was discovered in Iglu Server 0.13.0 and below. It is similar to CVE-2024-47214, but involves an authenticated endpoint. It can render Iglu Server completely unresponsive. If the operation of Iglu Server is not restored, event processing in the pipeline would eventually halt.

## References
- https://support.snowplow.io/hc/en-us/articles/26318139354909-Update-Critical-Snowplow-Security-Updates-Impact-on-Open-Source-Software-Users
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/47xxx/CVE-2024-47217.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-47217
