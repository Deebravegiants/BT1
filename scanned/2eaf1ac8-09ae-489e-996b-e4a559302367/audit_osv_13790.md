# [H] CVE-2018-2755

## Summary
Severity: High
Advisory: CVE-2018-2755
CVSS: 7.7 (CVSS:3.1/AV:L/AC:H/PR:N/UI:R/S:C/C:H/I:H/A:H)
Published: 2018-04-19
Source: https://osv.dev/vulnerability/CVE-2018-2755
Type: osv

## Details
Vulnerability in the MySQL Server component of Oracle MySQL (subcomponent: Server: Replication). Supported versions that are affected are 5.5.59 and prior, 5.6.39 and prior and 5.7.21 and prior. Difficult to exploit vulnerability allows unauthenticated attacker with logon to the infrastructure where MySQL Server executes to compromise MySQL Server. Successful attacks require human interaction from a person other than the attacker and while the vulnerability is in MySQL Server, attacks may significantly impact additional products. Successful attacks of this vulnerability can result in takeover of MySQL Server. CVSS 3.0 Base Score 7.7 (Confidentiality, Integrity and Availability impacts). CVSS Vector: (CVSS:3.0/AV:L/AC:H/PR:N/UI:R/S:C/C:H/I:H/A:H).

## References
- http://www.securityfocus.com/bid/103807
- http://www.securitytracker.com/id/1040698
- https://access.redhat.com/errata/RHSA-2018:1254
- https://access.redhat.com/errata/RHSA-2018:2439
- https://access.redhat.com/errata/RHSA-2018:2729
- https://access.redhat.com/errata/RHSA-2018:3655
- https://access.redhat.com/errata/RHSA-2019:1258
- https://lists.debian.org/debian-lts-announce/2018/04/msg00020.html
- https://lists.debian.org/debian-lts-announce/2018/06/msg00015.html
- https://security.gentoo.org/glsa/201908-24
- https://security.netapp.com/advisory/ntap-20180419-0002/
- https://usn.ubuntu.com/3629-1/
- https://usn.ubuntu.com/3629-2/
- https://usn.ubuntu.com/3629-3/
- https://www.debian.org/security/2018/dsa-4176
- https://www.debian.org/security/2018/dsa-4341
- http://www.oracle.com/technetwork/security-advisory/cpuapr2018-3678067.html
