# [M] CVE-2020-9391

## Summary
Severity: Medium
Advisory: CVE-2020-9391
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-02-25
Source: https://osv.dev/vulnerability/CVE-2020-9391
Type: osv

## Details
An issue was discovered in the Linux kernel 5.4 and 5.5 through 5.5.6 on the AArch64 architecture. It ignores the top byte in the address passed to the brk system call, potentially moving the memory break downwards when the application expects it to move upwards, aka CID-dcde237319e6. This has been observed to cause heap corruption with the GNU C Library malloc implementation.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/O4LH35HOPBJIKYHYFXMBBM75DN75PZHZ/
- https://security.netapp.com/advisory/ntap-20200313-0003/
- https://bugzilla.redhat.com/show_bug.cgi?id=1797052
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=dcde237319e626d1ec3c9d8b7613032f0fd4663a
- http://www.openwall.com/lists/oss-security/2020/02/25/6
