# [M] CVE-2014-0147

## Summary
Severity: Medium
Advisory: CVE-2014-0147
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-09-29
Source: https://osv.dev/vulnerability/CVE-2014-0147
Type: osv

## Details
Qemu before 1.6.2 block diver for the various disk image formats used by Bochs and for the QCOW version 2 format, are vulnerable to a possible crash caused by signed data types or a logic error while creating QCOW2 snapshots, which leads to incorrectly calling update_refcount() routine.

## References
- http://rhn.redhat.com/errata/RHSA-2014-0420.html
- http://rhn.redhat.com/errata/RHSA-2014-0421.html
- http://www.openwall.com/lists/oss-security/2014/03/26/8
- https://bugzilla.redhat.com/show_bug.cgi?id=1078848
- https://bugzilla.redhat.com/show_bug.cgi?id=1086717
- http://www.openwall.com/lists/oss-security/2014/03/26/8
- http://www.openwall.com/lists/oss-security/2014/03/26/8
- https://bugzilla.redhat.com/show_bug.cgi?id=1078848
- https://bugzilla.redhat.com/show_bug.cgi?id=1086717
- http://git.qemu.org/?p=qemu.git%3Ba=commitdiff%3Bh=246f65838d19db6db55bfb41117c35645a2c4789
