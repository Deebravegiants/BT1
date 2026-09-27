# [H] CVE-2021-1405

## Summary
Severity: High
Advisory: CVE-2021-1405
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-04-08
Source: https://osv.dev/vulnerability/CVE-2021-1405
Type: osv

## Details
A vulnerability in the email parsing module in Clam AntiVirus (ClamAV) Software version 0.103.1 and all prior versions could allow an unauthenticated, remote attacker to cause a denial of service condition on an affected device. The vulnerability is due to improper variable initialization that may result in an NULL pointer read. An attacker could exploit this vulnerability by sending a crafted email to an affected device. An exploit could allow the attacker to cause the ClamAV scanning process crash, resulting in a denial of service condition.

## References
- https://blog.clamav.net/2021/04/clamav-01032-security-patch-release.html
- https://lists.debian.org/debian-lts-announce/2021/04/msg00012.html
- https://security.gentoo.org/glsa/202104-07
