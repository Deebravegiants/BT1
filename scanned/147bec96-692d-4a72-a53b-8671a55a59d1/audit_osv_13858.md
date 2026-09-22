# [M] CVE-2018-3187

## Summary
Severity: Medium
Advisory: CVE-2018-3187
CVSS: 5.5 (CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:L/A:H)
Published: 2018-10-17
Source: https://osv.dev/vulnerability/CVE-2018-3187
Type: osv

## Details
Vulnerability in the MySQL Server component of Oracle MySQL (subcomponent: Server: Optimizer). Supported versions that are affected are 5.7.23 and prior and 8.0.12 and prior. Easily exploitable vulnerability allows high privileged attacker with network access via multiple protocols to compromise MySQL Server. Successful attacks of this vulnerability can result in unauthorized ability to cause a hang or frequently repeatable crash (complete DOS) of MySQL Server as well as unauthorized update, insert or delete access to some of MySQL Server accessible data. CVSS 3.0 Base Score 5.5 (Integrity and Availability impacts). CVSS Vector: (CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:L/A:H).

## References
- http://www.securityfocus.com/bid/105594
- http://www.securitytracker.com/id/1041888
- https://access.redhat.com/errata/RHSA-2018:3655
- https://security.netapp.com/advisory/ntap-20181018-0002/
- https://usn.ubuntu.com/3799-1/
- http://www.oracle.com/technetwork/security-advisory/cpuoct2018-4428296.html
