# [M] CVE-2022-32229

## Summary
Severity: Medium
Advisory: CVE-2022-32229
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2022-09-23
Source: https://osv.dev/vulnerability/CVE-2022-32229
Type: osv

## Details
A information disclosure vulnerability exists in Rockert.Chat <v5 due to /api/v1/chat.getThreadsList lack of sanitization of user inputs and can therefore leak private thread messages to unauthorized users via Mongo DB injection.

## References
- https://hackerone.com/reports/1446767
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/32xxx/CVE-2022-32229.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-32229
