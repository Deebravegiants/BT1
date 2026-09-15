# [M] CVE-2022-1508

## Summary
Severity: Medium
Advisory: CVE-2022-1508
CVSS: 6.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:H)
Published: 2022-08-31
Source: https://osv.dev/vulnerability/CVE-2022-1508
Type: osv

## Details
An out-of-bounds read flaw was found in the Linux kernel’s io_uring module in the way a user triggers the io_read() function with some special parameters. This flaw allows a local user to read some memory out of bounds.

## References
- https://access.redhat.com/security/cve/CVE-2022-1508
- https://bugzilla.redhat.com/show_bug.cgi?id=2075533
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=89c2b3b74918200e46699338d7bcc19b1ea12110
- https://ubuntu.com/security/CVE-2022-1508
