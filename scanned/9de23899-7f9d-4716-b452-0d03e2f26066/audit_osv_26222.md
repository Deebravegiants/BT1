# [M] nilfs2: fix potential use after free in nilfs_gccache_submit_read_data()

## Summary
Severity: Medium
Advisory: CVE-2023-52566
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-03-02
Source: https://osv.dev/vulnerability/CVE-2023-52566
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.30 <4.14.327, >=4.15.0 <4.19.296, >=4.20.0 <5.4.258, >=5.5.0 <5.10.198, >=5.11.0 <5.15.134, >=5.16.0 <6.1.56, >=6.2.0 <6.5.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

nilfs2: fix potential use after free in nilfs_gccache_submit_read_data()

In nilfs_gccache_submit_read_data(), brelse(bh) is called to drop the
reference count of bh when the call to nilfs_dat_translate() fails.  If
the reference count hits 0 and its owner page gets unlocked, bh may be
freed.  However, bh->b_page is dereferenced to put the page after that,
which may result in a use-after-free bug.  This patch moves the release
operation after unlocking and putting the page.

NOTE: The function in question is only called in GC, and in combination
with current userland tools, address translation using DAT does not occur
in that function, so the code path that causes this issue will not be
executed.  However, it is possible to run that code path by intentionally
modifying the userland GC library or by calling the GC ioctl directly.

[konishi.ryusuke@gmail.com: NOTE added to the commit log]

## References
- https://git.kernel.org/stable/c/193b5a1c6c67c36b430989dc063fe7ea4e200a33
- https://git.kernel.org/stable/c/28df4646ad8b433340772edc90ca709cdefc53e2
- https://git.kernel.org/stable/c/3936e8714907cd55e37c7cc50e50229e4a9042e8
- https://git.kernel.org/stable/c/7130a87ca32396eb9bf48b71a2d42259ae44c6c7
- https://git.kernel.org/stable/c/7ee29facd8a9c5a26079148e36bcf07141b3a6bc
- https://git.kernel.org/stable/c/980663f1d189eedafd18d80053d9cf3e2ceb5c8c
- https://git.kernel.org/stable/c/bb61224f6abc8e71bfdf06d7c984e23460875f5b
- https://git.kernel.org/stable/c/fb1084e63ee56958b0a56e17a50a4fd86445b9c1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52566.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52566
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
