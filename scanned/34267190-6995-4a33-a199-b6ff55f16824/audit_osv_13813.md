# [M] CVE-2018-2812

## Summary
Severity: Medium
Advisory: CVE-2018-2812
CVSS: 5.5 (CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:L/A:H)
Published: 2018-04-19
Source: https://osv.dev/vulnerability/CVE-2018-2812
Type: osv

## Details
Vulnerability in the MySQL Server component of Oracle MySQL (subcomponent: Server: Optimizer). Supported versions that are affected are 5.7.21 and prior. Easily exploitable vulnerability allows high privileged attacker with network access via multiple protocols to compromise MySQL Server. Successful attacks of this vulnerability can result in unauthorized ability to cause a hang or frequently repeatable crash (complete DOS) of MySQL Server as well as unauthorized update, insert or delete access to some of MySQL Server accessible data. CVSS 3.0 Base Score 5.5 (Integrity and Availability impacts). CVSS Vector: (CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:L/A:H).

## References
- http://www.securityfocus.com/bid/103836
- http://www.securitytracker.com/id/1040698
- https://access.redhat.com/errata/RHSA-2018:3655
- https://security.netapp.com/advisory/ntap-20180419-0002/
- https://usn.ubuntu.com/3629-1/
- https://usn.ubuntu.com/3629-3/
- http://www.oracle.com/technetwork/security-advisory/cpuapr2018-3678067.html
