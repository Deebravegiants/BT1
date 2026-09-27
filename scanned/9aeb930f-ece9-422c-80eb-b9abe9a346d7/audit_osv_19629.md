# [M] CVE-2021-22960

## Summary
Severity: Medium
Advisory: CVE-2021-22960
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2021-11-03
Source: https://osv.dev/vulnerability/CVE-2021-22960
Type: osv

## Details
The parse function in llhttp < 2.1.4 and < 6.0.6. ignores chunk extensions when parsing the body of chunked requests. This leads to HTTP Request Smuggling (HRS) under certain conditions.

## References
- https://www.debian.org/security/2022/dsa-5170
- https://hackerone.com/reports/1238099
- https://www.oracle.com/security-alerts/cpujan2022.html
