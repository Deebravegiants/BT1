# [H] CVE-2020-3481

## Summary
Severity: High
Advisory: CVE-2020-3481
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-07-20
Source: https://osv.dev/vulnerability/CVE-2020-3481
Type: osv

## Details
A vulnerability in the EGG archive parsing module in Clam AntiVirus (ClamAV) Software versions 0.102.0 - 0.102.3 could allow an unauthenticated, remote attacker to cause a denial of service condition on an affected device. The vulnerability is due to a null pointer dereference. An attacker could exploit this vulnerability by sending a crafted EGG file to an affected device. An exploit could allow the attacker to cause the ClamAV scanning process crash, resulting in a denial of service condition.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/IJ67VH37NCG25PICGWFWZHSVG7PBT7MC/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/QM7EXJHDEZJLWM2NKH6TCDXOBP5NNYIN/
- https://blog.clamav.net/2020/07/clamav-01024-security-patch-released.html
- https://lists.debian.org/debian-lts-announce/2020/08/msg00010.html
- https://security.gentoo.org/glsa/202007-23
- https://usn.ubuntu.com/4435-1/
- https://usn.ubuntu.com/4435-2/
