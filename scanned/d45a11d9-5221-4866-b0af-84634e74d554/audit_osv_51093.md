# [M] CVE-2021-20261

## Summary
Severity: Medium
Advisory: CVE-2021-20261
CVSS: 6.4 (CVSS:3.1/AV:L/AC:H/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-03-11
Source: https://osv.dev/vulnerability/CVE-2021-20261
Type: osv

## Details
A race condition was found in the Linux kernels implementation of the floppy disk drive controller driver software. The impact of this issue is lessened by the fact that the default permissions on the floppy device (/dev/fd0) are restricted to root. If the permissions on the device have changed the impact changes greatly. In the default configuration root (or equivalent) permissions are required to attack this flaw.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1932150
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=a0c80efe5956ccce9fe7ae5c78542578c07bc20a
