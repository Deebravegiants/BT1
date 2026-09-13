# [M] CVE-2017-3454

## Summary
Severity: Medium
Advisory: CVE-2017-3454
CVSS: 5.5 (CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:L/A:H)
Published: 2017-04-24
Source: https://osv.dev/vulnerability/CVE-2017-3454
Type: osv

## Details
Vulnerability in the MySQL Server component of Oracle MySQL (subcomponent: Server: InnoDB). Supported versions that are affected are 5.7.17 and earlier. Easily "exploitable" vulnerability allows high privileged attacker with network access via multiple protocols to compromise MySQL Server. Successful attacks of this vulnerability can result in unauthorized ability to cause a hang or frequently repeatable crash (complete DOS) of MySQL Server as well as unauthorized update, insert or delete access to some of MySQL Server accessible data. CVSS 3.0 Base Score 5.5 (Integrity and Availability impacts). CVSS Vector: (CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:L/A:H).

## References
- http://www.securitytracker.com/id/1038287
- http://www.securityfocus.com/bid/97791
- https://access.redhat.com/errata/RHSA-2017:2886
- http://www.oracle.com/technetwork/security-advisory/cpuapr2017-3236618.html
