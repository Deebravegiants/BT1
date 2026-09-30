# [M] CVE-2016-8660

## Summary
Severity: Medium
Advisory: CVE-2016-8660
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-10-16
Source: https://osv.dev/vulnerability/CVE-2016-8660
Type: osv

## Details
The XFS subsystem in the Linux kernel through 4.8.2 allows local users to cause a denial of service (fdatasync failure and system hang) by using the vfs syscall group in the trinity program, related to a "page lock order bug in the XFS seek hole/data implementation."

## References
- http://www.securityfocus.com/bid/93558
- https://bugzilla.redhat.com/show_bug.cgi?id=1384851
- http://www.openwall.com/lists/oss-security/2016/10/13/8
