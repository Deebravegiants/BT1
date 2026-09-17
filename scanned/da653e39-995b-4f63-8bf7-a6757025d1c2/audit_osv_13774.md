# [M] CVE-2018-2583

## Summary
Severity: Medium
Advisory: CVE-2018-2583
CVSS: 6.8 (CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:C/C:N/I:N/A:H)
Published: 2018-01-18
Source: https://osv.dev/vulnerability/CVE-2018-2583
Type: osv

## Details
Vulnerability in the MySQL Server component of Oracle MySQL (subcomponent: Stored Procedure). Supported versions that are affected are 5.6.38 and prior and 5.7.20 and prior. Easily exploitable vulnerability allows high privileged attacker with network access via multiple protocols to compromise MySQL Server. While the vulnerability is in MySQL Server, attacks may significantly impact additional products. Successful attacks of this vulnerability can result in unauthorized ability to cause a hang or frequently repeatable crash (complete DOS) of MySQL Server. CVSS 3.0 Base Score 6.8 (Availability impacts). CVSS Vector: (CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:C/C:N/I:N/A:H).

## References
- https://usn.ubuntu.com/3537-1/
- http://www.securityfocus.com/bid/102708
- http://www.securitytracker.com/id/1040216
- https://access.redhat.com/errata/RHSA-2018:0586
- https://access.redhat.com/errata/RHSA-2018:0587
- https://security.netapp.com/advisory/ntap-20180117-0002/
- http://www.oracle.com/technetwork/security-advisory/cpujan2018-3236628.html
