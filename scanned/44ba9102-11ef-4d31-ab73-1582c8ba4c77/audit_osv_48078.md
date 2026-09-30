# [H] CVE-2017-17854

## Summary
Severity: High
Advisory: CVE-2017-17854
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-12-27
Source: https://osv.dev/vulnerability/CVE-2017-17854
Type: osv

## Details
kernel/bpf/verifier.c in the Linux kernel through 4.14.8 allows local users to cause a denial of service (integer overflow and memory corruption) or possibly have unspecified other impact by leveraging unrestricted integer values for pointer arithmetic.

## References
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=bb7f0f989ca7de1153bd128a40a71709e339fa03
- https://github.com/torvalds/linux/commit/bb7f0f989ca7de1153bd128a40a71709e339fa03
- http://www.openwall.com/lists/oss-security/2017/12/21/2
