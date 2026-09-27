# [M] CVE-2018-3081

## Summary
Severity: Medium
Advisory: CVE-2018-3081
CVSS: 5.0 (CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:N/I:L/A:H)
Published: 2018-07-18
Source: https://osv.dev/vulnerability/CVE-2018-3081
Type: osv

## Details
Vulnerability in the MySQL Client component of Oracle MySQL (subcomponent: Client programs). Supported versions that are affected are 5.5.60 and prior, 5.6.40 and prior, 5.7.22 and prior and 8.0.11 and prior. Difficult to exploit vulnerability allows high privileged attacker with network access via multiple protocols to compromise MySQL Client. Successful attacks of this vulnerability can result in unauthorized ability to cause a hang or frequently repeatable crash (complete DOS) of MySQL Client as well as unauthorized update, insert or delete access to some of MySQL Client accessible data. CVSS 3.0 Base Score 5.0 (Integrity and Availability impacts). CVSS Vector: (CVSS:3.0/AV:N/AC:H/PR:H/UI:N/S:U/C:N/I:L/A:H).

## References
- http://www.securityfocus.com/bid/104779
- http://www.securitytracker.com/id/1041294
- https://access.redhat.com/errata/RHSA-2018:3655
- https://access.redhat.com/errata/RHSA-2019:1258
- https://access.redhat.com/errata/RHSA-2019:2327
- https://lists.debian.org/debian-lts-announce/2018/11/msg00004.html
- https://security.netapp.com/advisory/ntap-20180726-0002/
- https://usn.ubuntu.com/3725-1/
- https://usn.ubuntu.com/3725-2/
- https://www.debian.org/security/2018/dsa-4341
- http://www.oracle.com/technetwork/security-advisory/cpujul2018-4258247.html
