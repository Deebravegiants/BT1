# [H] CVE-2017-16996

## Summary
Severity: High
Advisory: CVE-2017-16996
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-12-27
Source: https://osv.dev/vulnerability/CVE-2017-16996
Type: osv

## Details
kernel/bpf/verifier.c in the Linux kernel through 4.14.8 allows local users to cause a denial of service (memory corruption) or possibly have unspecified other impact by leveraging register truncation mishandling.

## References
- http://www.securityfocus.com/bid/102267
- https://bugs.chromium.org/p/project-zero/issues/detail?id=1454
- http://openwall.com/lists/oss-security/2017/12/21/2
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=0c17d1d2c61936401f4702e1846e2c19b200f958
- https://github.com/torvalds/linux/commit/0c17d1d2c61936401f4702e1846e2c19b200f958
