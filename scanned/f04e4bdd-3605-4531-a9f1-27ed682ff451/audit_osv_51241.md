# [H] CVE-2021-21806

## Summary
Severity: High
Advisory: CVE-2021-21806
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-07-08
Source: https://osv.dev/vulnerability/CVE-2021-21806
Type: osv

## Details
An exploitable use-after-free vulnerability exists in WebKitGTK browser version 2.30.3 x64. A specially crafted HTML web page can cause a use-after-free condition, resulting in remote code execution. The victim needs to visit a malicious web site to trigger the vulnerability.

## References
- http://www.openwall.com/lists/oss-security/2021/07/23/1
- https://talosintelligence.com/vulnerability_reports/TALOS-2020-1214
