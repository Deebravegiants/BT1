# [H] CVE-2020-3327

## Summary
Severity: High
Advisory: CVE-2020-3327
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-05-13
Source: https://osv.dev/vulnerability/CVE-2020-3327
Type: osv

## Details
A vulnerability in the ARJ archive parsing module in Clam AntiVirus (ClamAV) Software versions 0.102.2 could allow an unauthenticated, remote attacker to cause a denial of service condition on an affected device. The vulnerability is due to a heap buffer overflow read. An attacker could exploit this vulnerability by sending a crafted ARJ file to an affected device. An exploit could allow the attacker to cause the ClamAV scanning process crash, resulting in a denial of service condition.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/L5YWYT27SBTV4RZSGFHIQUI4LQVFASWS/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/QM7EXJHDEZJLWM2NKH6TCDXOBP5NNYIN/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/3BMTC7I5LGY4FCIZLHPNC4WWC6VNLFER/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/IJ67VH37NCG25PICGWFWZHSVG7PBT7MC/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ROBJOGJOT44MVDX7RQEACYHQN4LYW5RK/
- https://usn.ubuntu.com/4435-2/
- https://lists.debian.org/debian-lts-announce/2020/05/msg00018.html
- https://security.gentoo.org/glsa/202007-23
- https://usn.ubuntu.com/4370-2/
- https://usn.ubuntu.com/4435-1/
- https://blog.clamav.net/2020/05/clamav-01023-security-patch-released.html
- https://lists.debian.org/debian-lts-announce/2020/08/msg00010.html
- https://usn.ubuntu.com/4370-1/
