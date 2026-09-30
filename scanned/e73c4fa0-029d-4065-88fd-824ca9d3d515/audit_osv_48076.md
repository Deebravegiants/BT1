# [H] CVE-2017-17852

## Summary
Severity: High
Advisory: CVE-2017-17852
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-12-27
Source: https://osv.dev/vulnerability/CVE-2017-17852
Type: osv

## Details
kernel/bpf/verifier.c in the Linux kernel through 4.14.8 allows local users to cause a denial of service (memory corruption) or possibly have unspecified other impact by leveraging mishandling of 32-bit ALU ops.

## References
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=468f6eafa6c44cb2c5d8aad35e12f06c240a812a
- https://github.com/torvalds/linux/commit/468f6eafa6c44cb2c5d8aad35e12f06c240a812a
- http://www.openwall.com/lists/oss-security/2017/12/21/2
