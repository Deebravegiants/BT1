# [M] CVE-2008-2544

## Summary
Severity: Medium
Advisory: CVE-2008-2544
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2021-05-27
Source: https://osv.dev/vulnerability/CVE-2008-2544
Type: osv

## Details
Mounting /proc filesystem via chroot command silently mounts it in read-write mode. The user could bypass the chroot environment and gain write access to files, he would never have otherwise.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=213135
- https://bugzilla.redhat.com/show_bug.cgi?id=213135
- https://bugzilla.redhat.com/show_bug.cgi?id=213135
