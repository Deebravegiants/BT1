# [M] CVE-2018-1106

## Summary
Severity: Medium
Advisory: CVE-2018-1106
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2018-04-23
Source: https://osv.dev/vulnerability/CVE-2018-1106
Type: osv

## Details
An authentication bypass flaw has been found in PackageKit before 1.1.10 that allows users without administrator privileges to install signed packages. A local attacker can use this vulnerability to install vulnerable packages to further compromise a system.

## References
- http://www.openwall.com/lists/oss-security/2018/04/23/3
- https://access.redhat.com/errata/RHSA-2018:1224
- https://usn.ubuntu.com/3634-1/
- https://www.debian.org/security/2018/dsa-4207
- https://bugzilla.redhat.com/show_bug.cgi?id=1565992
