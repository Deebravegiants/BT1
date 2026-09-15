# [H] CVE-2018-6553

## Summary
Severity: High
Advisory: CVE-2018-6553
CVSS: 8.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2018-08-10
Source: https://osv.dev/vulnerability/CVE-2018-6553
Type: osv

## Details
The CUPS AppArmor profile incorrectly confined the dnssd backend due to use of hard links. A local attacker could possibly use this issue to escape confinement. This flaw affects versions prior to 2.2.7-1ubuntu2.1 in Ubuntu 18.04 LTS, prior to 2.2.4-7ubuntu3.1 in Ubuntu 17.10, prior to 2.1.3-4ubuntu0.5 in Ubuntu 16.04 LTS, and prior to 1.7.2-0ubuntu1.10 in Ubuntu 14.04 LTS.

## References
- https://security.gentoo.org/glsa/201908-08
- https://usn.ubuntu.com/usn/usn-3713-1
- https://www.debian.org/security/2018/dsa-4243
- https://lists.debian.org/debian-lts-announce/2018/07/msg00014.html
