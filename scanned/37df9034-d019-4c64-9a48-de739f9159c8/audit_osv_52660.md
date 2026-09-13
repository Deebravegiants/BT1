# [M] CVE-2022-0168

## Summary
Severity: Medium
Advisory: CVE-2022-0168
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-08-26
Source: https://osv.dev/vulnerability/CVE-2022-0168
Type: osv

## Details
A denial of service (DOS) issue was found in the Linux kernel’s smb2_ioctl_query_info function in the fs/cifs/smb2ops.c Common Internet File System (CIFS) due to an incorrect return from the memdup_user function. This flaw allows a local, privileged (CAP_SYS_ADMIN) attacker to crash the system.

## References
- https://access.redhat.com/security/cve/CVE-2022-0168
- https://bugzilla.redhat.com/show_bug.cgi?id=2037386
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=d6f5e358452479fa8a773b5c6ccc9e4ec5a20880
