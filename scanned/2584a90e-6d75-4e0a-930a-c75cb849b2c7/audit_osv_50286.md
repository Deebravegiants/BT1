# [M] CVE-2020-10773

## Summary
Severity: Medium
Advisory: CVE-2020-10773
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-09-10
Source: https://osv.dev/vulnerability/CVE-2020-10773
Type: osv

## Details
A stack information leak flaw was found in s390/s390x in the Linux kernel’s memory manager functionality, where it incorrectly writes to the /proc/sys/vm/cmm_timeout file. This flaw allows a local user to see the kernel data.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2020-10773
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=b8e51a6a9db94bc1fb18ae831b3dab106b5a4b5f
