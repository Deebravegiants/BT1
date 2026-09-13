# [M] CVE-2018-3251

## Summary
Severity: Medium
Advisory: CVE-2018-3251
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-10-17
Source: https://osv.dev/vulnerability/CVE-2018-3251
Type: osv

## Details
Vulnerability in the MySQL Server component of Oracle MySQL (subcomponent: InnoDB). Supported versions that are affected are 5.6.41 and prior, 5.7.23 and prior and 8.0.12 and prior. Easily exploitable vulnerability allows low privileged attacker with network access via multiple protocols to compromise MySQL Server. Successful attacks of this vulnerability can result in unauthorized ability to cause a hang or frequently repeatable crash (complete DOS) of MySQL Server. CVSS 3.0 Base Score 6.5 (Availability impacts). CVSS Vector: (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H).

## References
- http://www.securityfocus.com/bid/105600
- http://www.securitytracker.com/id/1041888
- https://access.redhat.com/errata/RHSA-2018:3655
- https://access.redhat.com/errata/RHSA-2019:1258
- https://lists.debian.org/debian-lts-announce/2018/11/msg00007.html
- https://security.gentoo.org/glsa/201908-24
- https://security.netapp.com/advisory/ntap-20181018-0002/
- https://usn.ubuntu.com/3799-1/
- https://www.debian.org/security/2018/dsa-4341
- http://www.oracle.com/technetwork/security-advisory/cpuoct2018-4428296.html
