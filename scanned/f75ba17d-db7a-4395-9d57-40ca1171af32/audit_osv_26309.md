# [H] fs/jfs: Add check for negative db_l2nbperpage

## Summary
Severity: High
Advisory: CVE-2023-52810
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2023-52810
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <4.14.331, >=4.15.0 <4.19.300, >=4.20.0 <5.4.262, >=5.5.0 <5.10.202, >=5.11.0 <5.15.140, >=5.16.0 <6.1.64, >=6.2.0 <6.5.13, >=6.6.0 <6.6.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

fs/jfs: Add check for negative db_l2nbperpage

l2nbperpage is log2(number of blks per page), and the minimum legal
value should be 0, not negative.

In the case of l2nbperpage being negative, an error will occur
when subsequently used as shift exponent.

Syzbot reported this bug:

UBSAN: shift-out-of-bounds in fs/jfs/jfs_dmap.c:799:12
shift exponent -16777216 is negative

## References
- https://git.kernel.org/stable/c/0cb567e727339a192f9fd0db00781d73a91d15a6
- https://git.kernel.org/stable/c/1a7c53fdea1d189087544d9a606d249e93c4934b
- https://git.kernel.org/stable/c/491085258185ffc4fb91555b0dba895fe7656a45
- https://git.kernel.org/stable/c/524b4f203afcf87accfe387e846f33f916f0c907
- https://git.kernel.org/stable/c/525b861a008143048535011f3816d407940f4bfa
- https://git.kernel.org/stable/c/5f148b16972e5f4592629b244d5109b15135f53f
- https://git.kernel.org/stable/c/8f2964df6bfce9d92d81ca552010b8677af8d9dc
- https://git.kernel.org/stable/c/a81a56b4cbe3142cc99f6b98e8f9b3a631c768e1
- https://git.kernel.org/stable/c/cc61fcf7d1c99f148fe8ddfb5c6ed0bb75861f01
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52810.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52810
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
