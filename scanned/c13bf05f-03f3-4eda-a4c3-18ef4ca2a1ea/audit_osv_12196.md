# [H] CVE-2018-10875

## Summary
Severity: High
Advisory: CVE-2018-10875
Aliases: GHSA-fc4h-467w-46rh, PYSEC-2018-43
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-07-13
Source: https://osv.dev/vulnerability/CVE-2018-10875
Type: osv

## Details
A flaw was found in ansible. ansible.cfg is read from the current working directory which can be altered to make it point to a plugin or a module path under the control of an attacker, thus allowing the attacker to execute arbitrary code.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-04/msg00021.html
- http://www.securitytracker.com/id/1041396
- https://access.redhat.com/errata/RHBA-2018:3788
- https://access.redhat.com/errata/RHSA-2018:2150
- https://access.redhat.com/errata/RHSA-2018:2151
- https://access.redhat.com/errata/RHSA-2018:2152
- https://access.redhat.com/errata/RHSA-2018:2166
- https://access.redhat.com/errata/RHSA-2018:2321
- https://access.redhat.com/errata/RHSA-2018:2585
- https://access.redhat.com/errata/RHSA-2019:0054
- https://lists.debian.org/debian-lts-announce/2019/09/msg00016.html
- https://usn.ubuntu.com/4072-1/
- https://www.debian.org/security/2019/dsa-4396
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-10875
