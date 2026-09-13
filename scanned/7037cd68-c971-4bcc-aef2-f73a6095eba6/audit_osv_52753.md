# [H] CVE-2022-1011

## Summary
Severity: High
Advisory: CVE-2022-1011
Aliases: A-226679409, PUB-A-226679409
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-03-18
Source: https://osv.dev/vulnerability/CVE-2022-1011
Type: osv

## Details
A use-after-free flaw was found in the Linux kernel’s FUSE filesystem in the way a user triggers write(). This flaw allows a local user to gain unauthorized access to data from the FUSE filesystem, resulting in privilege escalation.

## References
- https://www.debian.org/security/2022/dsa-5173
- https://www.oracle.com/security-alerts/cpujul2022.html
- https://git.kernel.org/pub/scm/linux/kernel/git/mszeredi/fuse.git/commit/?h=for-next
- https://lists.debian.org/debian-lts-announce/2022/07/msg00000.html
- https://bugzilla.redhat.com/show_bug.cgi?id=2064855
