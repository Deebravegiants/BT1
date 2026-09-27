# [H] CVE-2021-1252

## Summary
Severity: High
Advisory: CVE-2021-1252
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-04-08
Source: https://osv.dev/vulnerability/CVE-2021-1252
Type: osv

## Details
A vulnerability in the Excel XLM macro parsing module in Clam AntiVirus (ClamAV) Software versions 0.103.0 and 0.103.1 could allow an unauthenticated, remote attacker to cause a denial of service condition on an affected device. The vulnerability is due to improper error handling that may result in an infinite loop. An attacker could exploit this vulnerability by sending a crafted Excel file to an affected device. An exploit could allow the attacker to cause the ClamAV scanning process hang, resulting in a denial of service condition.

## References
- https://blog.clamav.net/2021/04/clamav-01032-security-patch-release.html
