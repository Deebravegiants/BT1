# [H] dm flakey: don't corrupt the zero page

## Summary
Severity: High
Advisory: CVE-2023-54317
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-30
Source: https://osv.dev/vulnerability/CVE-2023-54317
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <4.14.308, >=4.15.0 <4.19.276, >=4.20.0 <5.4.235, >=5.0.0 <5.10.173, >=5.5.0 <5.15.99, >=5.11.0 <6.1.16, >=5.16.0 <6.2.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

dm flakey: don't corrupt the zero page

When we need to zero some range on a block device, the function
__blkdev_issue_zero_pages submits a write bio with the bio vector pointing
to the zero page. If we use dm-flakey with corrupt bio writes option, it
will corrupt the content of the zero page which results in crashes of
various userspace programs. Glibc assumes that memory returned by mmap is
zeroed and it uses it for calloc implementation; if the newly mapped
memory is not zeroed, calloc will return non-zeroed memory.

Fix this bug by testing if the page is equal to ZERO_PAGE(0) and
avoiding the corruption in this case.

## References
- https://git.kernel.org/stable/c/3c4a56ef7c538d16c1738ba0ccea9e7146105b5a
- https://git.kernel.org/stable/c/63d31617883d64b43b0e2d529f0751f40713ecae
- https://git.kernel.org/stable/c/98e311be44dbe31ad9c42aa067b2359bac451fda
- https://git.kernel.org/stable/c/b7f8892f672222dbfcc721f51edc03963212b249
- https://git.kernel.org/stable/c/be360c83f2d810493c04f999d69ec9152981e0c0
- https://git.kernel.org/stable/c/f2b478228bfdd11e358c5bc197561331f5d5c394
- https://git.kernel.org/stable/c/f50714b57aecb6b3dc81d578e295f86d9c73f078
- https://git.kernel.org/stable/c/ff60b2bb680ebcaf8890814dd51084a022891469
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/54xxx/CVE-2023-54317.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-54317
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
