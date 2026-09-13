# [H] CVE-2022-20698

## Summary
Severity: High
Advisory: CVE-2022-20698
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-01-14
Source: https://osv.dev/vulnerability/CVE-2022-20698
Type: osv

## Details
A vulnerability in the OOXML parsing module in Clam AntiVirus (ClamAV) Software version 0.104.1 and LTS version 0.103.4 and prior versions could allow an unauthenticated, remote attacker to cause a denial of service condition on an affected device. The vulnerability is due to improper checks that may result in an invalid pointer read. An attacker could exploit this vulnerability by sending a crafted OOXML file to an affected device. An exploit could allow the attacker to cause the ClamAV scanning process to crash, resulting in a denial of service condition.

## References
- https://security.gentoo.org/glsa/202310-01
- https://blog.clamav.net/2022/01/clamav-01035-and-01042-security-patch.html
