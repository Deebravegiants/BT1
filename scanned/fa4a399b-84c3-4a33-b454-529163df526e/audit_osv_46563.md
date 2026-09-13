# [H] CVE-2013-4536

## Summary
Severity: High
Advisory: CVE-2013-4536
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-05-28
Source: https://osv.dev/vulnerability/CVE-2013-4536
Type: osv

## Details
An user able to alter the savevm data (either on the disk or over the wire during migration) could use this flaw to to corrupt QEMU process memory on the (destination) host, which could potentially result in arbitrary code execution on the host with the privileges of the QEMU process.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1066401
- https://security.netapp.com/advisory/ntap-20210727-0002/
- https://bugzilla.redhat.com/show_bug.cgi?id=1066401
- https://bugzilla.redhat.com/show_bug.cgi?id=1066401
