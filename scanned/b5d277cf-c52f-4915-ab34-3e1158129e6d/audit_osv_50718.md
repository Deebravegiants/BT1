# [H] CVE-2020-3341

## Summary
Severity: High
Advisory: CVE-2020-3341
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-05-13
Source: https://osv.dev/vulnerability/CVE-2020-3341
Type: osv

## Details
A vulnerability in the PDF archive parsing module in Clam AntiVirus (ClamAV) Software versions 0.101 - 0.102.2 could allow an unauthenticated, remote attacker to cause a denial of service condition on an affected device. The vulnerability is due to a stack buffer overflow read. An attacker could exploit this vulnerability by sending a crafted PDF file to an affected device. An exploit could allow the attacker to cause the ClamAV scanning process crash, resulting in a denial of service condition.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ROBJOGJOT44MVDX7RQEACYHQN4LYW5RK/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/3BMTC7I5LGY4FCIZLHPNC4WWC6VNLFER/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/L5YWYT27SBTV4RZSGFHIQUI4LQVFASWS/
- https://usn.ubuntu.com/4370-1/
- https://usn.ubuntu.com/4370-2/
- https://blog.clamav.net/2020/05/clamav-01023-security-patch-released.html
- https://lists.debian.org/debian-lts-announce/2020/05/msg00018.html
