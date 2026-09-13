# [M] CVE-2023-28358

## Summary
Severity: Medium
Advisory: CVE-2023-28358
CVSS: 6.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N)
Published: 2023-05-11
Source: https://osv.dev/vulnerability/CVE-2023-28358
Type: osv

## Details
A vulnerability has been discovered in Rocket.Chat where a markdown parsing issue in the "Search Messages" feature allows the insertion of malicious tags. This can be exploited on servers with content security policy disabled possible leading to some issues attacks like account takeover.

## References
- https://hackerone.com/reports/1781131
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/28xxx/CVE-2023-28358.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-28358
