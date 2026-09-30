# [H] CVE-2024-0775

## Summary
Severity: High
Advisory: CVE-2024-0775
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2024-01-22
Source: https://osv.dev/vulnerability/CVE-2024-0775
Type: osv

## Details
A use-after-free flaw was found in the __ext4_remount in fs/ext4/super.c in ext4 in the Linux kernel. This flaw allows a local user to cause an information leak problem while freeing the old quota file names before a potential failure, leading to a use-after-free.

## References
- https://access.redhat.com/security/cve/CVE-2024-0775
- https://bugzilla.redhat.com/show_bug.cgi?id=2259414
- https://scm.linefinity.com/common/linux-stable/commit/4c0b4818b1f636bc96359f7817a2d8bab6370162
