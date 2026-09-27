# [M] CVE-2018-3174

## Summary
Severity: Medium
Advisory: CVE-2018-3174
CVSS: 5.3 (CVSS:3.1/AV:L/AC:H/PR:H/UI:N/S:C/C:N/I:N/A:H)
Published: 2018-10-17
Source: https://osv.dev/vulnerability/CVE-2018-3174
Type: osv

## Details
Vulnerability in the MySQL Server component of Oracle MySQL (subcomponent: Client programs). Supported versions that are affected are 5.5.61 and prior, 5.6.41 and prior, 5.7.23 and prior and 8.0.12 and prior. Difficult to exploit vulnerability allows high privileged attacker with logon to the infrastructure where MySQL Server executes to compromise MySQL Server. While the vulnerability is in MySQL Server, attacks may significantly impact additional products. Successful attacks of this vulnerability can result in unauthorized ability to cause a hang or frequently repeatable crash (complete DOS) of MySQL Server. CVSS 3.0 Base Score 5.3 (Availability impacts). CVSS Vector: (CVSS:3.0/AV:L/AC:H/PR:H/UI:N/S:C/C:N/I:N/A:H).

## References
- http://www.securityfocus.com/bid/105612
- http://www.securitytracker.com/id/1041888
- https://access.redhat.com/errata/RHSA-2018:3655
- https://access.redhat.com/errata/RHSA-2019:1258
- https://lists.debian.org/debian-lts-announce/2018/11/msg00004.html
- https://lists.debian.org/debian-lts-announce/2018/11/msg00007.html
- https://security.gentoo.org/glsa/201908-24
- https://security.netapp.com/advisory/ntap-20181018-0002/
- https://usn.ubuntu.com/3799-1/
- https://usn.ubuntu.com/3799-2/
- https://www.debian.org/security/2018/dsa-4341
- http://www.oracle.com/technetwork/security-advisory/cpuoct2018-4428296.html
