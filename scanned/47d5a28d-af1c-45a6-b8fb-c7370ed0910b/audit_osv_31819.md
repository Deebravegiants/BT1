# [H] block: don't revert iter for -EIOCBQUEUED

## Summary
Severity: High
Advisory: CVE-2025-21832
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-03-06
Source: https://osv.dev/vulnerability/CVE-2025-21832
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.17.0 <6.1.129, >=6.2.0 <6.6.78, >=6.7.0 <6.12.14, >=6.13.0 <6.13.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

block: don't revert iter for -EIOCBQUEUED

blkdev_read_iter() has a few odd checks, like gating the position and
count adjustment on whether or not the result is bigger-than-or-equal to
zero (where bigger than makes more sense), and not checking the return
value of blkdev_direct_IO() before doing an iov_iter_revert(). The
latter can lead to attempting to revert with a negative value, which
when passed to iov_iter_revert() as an unsigned value will lead to
throwing a WARN_ON() because unroll is bigger than MAX_RW_COUNT.

Be sane and don't revert for -EIOCBQUEUED, like what is done in other
spots.

## References
- https://git.kernel.org/stable/c/68f16d3034a06661245ecd22f0d586a8b4e7c473
- https://git.kernel.org/stable/c/6c26619effb1b4cb7d20b4e666ab8f71f6a53ccb
- https://git.kernel.org/stable/c/84671b0630ccb46ae9f1f99a45c7d63ffcd6a474
- https://git.kernel.org/stable/c/a58f136bad29f9ae721a29d98c042fddbee22f77
- https://git.kernel.org/stable/c/b13ee668e8280ca5b07f8ce2846b9957a8a10853
- https://lists.debian.org/debian-lts-announce/2025/03/msg00028.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21832.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21832
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
