# [H] CVE-2017-17855

## Summary
Severity: High
Advisory: CVE-2017-17855
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-12-27
Source: https://osv.dev/vulnerability/CVE-2017-17855
Type: osv

## Details
kernel/bpf/verifier.c in the Linux kernel through 4.14.8 allows local users to cause a denial of service (memory corruption) or possibly have unspecified other impact by leveraging improper use of pointers in place of scalars.

## References
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=179d1c5602997fef5a940c6ddcf31212cbfebd14
- http://www.openwall.com/lists/oss-security/2017/12/21/2
- https://github.com/torvalds/linux/commit/179d1c5602997fef5a940c6ddcf31212cbfebd14
