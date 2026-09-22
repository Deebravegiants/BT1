# [H] CVE-2024-47213

## Summary
Severity: High
Advisory: CVE-2024-47213
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-04-03
Source: https://osv.dev/vulnerability/CVE-2024-47213
Type: osv

## Details
An issue was discovered affecting Enrich 5.1.0 and below. It involves sending a maliciously crafted Snowplow event to the pipeline. Upon receiving this event and trying to validate it, Enrich crashes and attempts to restart indefinitely. As a result, event processing would be halted.

## References
- https://support.snowplow.io/hc/en-us/articles/26318139354909-Update-Critical-Snowplow-Security-Updates-Impact-on-Open-Source-Software-Users
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/47xxx/CVE-2024-47213.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-47213
