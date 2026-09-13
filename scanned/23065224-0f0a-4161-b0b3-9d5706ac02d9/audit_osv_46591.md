# [M] CVE-2014-0146

## Summary
Severity: Medium
Advisory: CVE-2014-0146
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-08-10
Source: https://osv.dev/vulnerability/CVE-2014-0146
Type: osv

## Details
The qcow2_open function in the (block/qcow2.c) in QEMU before 1.7.2 and 2.x before 2.0.0 allows local users to cause a denial of service (NULL pointer dereference) via a crafted image which causes an error, related to the initialization of the snapshot_offset and nb_snapshots fields.

## References
- http://rhn.redhat.com/errata/RHSA-2014-0420.html
- http://rhn.redhat.com/errata/RHSA-2014-0421.html
- http://www.debian.org/security/2014/dsa-3044
- http://www.openwall.com/lists/oss-security/2014/03/26/8
- https://bugzilla.redhat.com/show_bug.cgi?id=1078232
- http://www.openwall.com/lists/oss-security/2014/03/26/8
- https://bugzilla.redhat.com/show_bug.cgi?id=1078232
- http://git.qemu.org/?p=qemu.git%3Ba=commit%3Bh=11b128f4062dd7f89b14abc8877ff20d41b28be9
