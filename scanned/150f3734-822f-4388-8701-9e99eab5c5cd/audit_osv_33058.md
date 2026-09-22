# [H] gfs2: No more self recovery

## Summary
Severity: High
Advisory: CVE-2025-38659
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-08-22
Source: https://osv.dev/vulnerability/CVE-2025-38659
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.7.0 <5.15.209, >=5.16.0 <6.1.167, >=6.2.0 <6.6.102, >=6.7.0 <6.12.42, >=6.13.0 <6.15.10, >=6.16.0 <6.16.1

## Details
In the Linux kernel, the following vulnerability has been resolved:

gfs2: No more self recovery

When a node withdraws and it turns out that it is the only node that has
the filesystem mounted, gfs2 currently tries to replay the local journal
to bring the filesystem back into a consistent state.  Not only is that
a very bad idea, it has also never worked because gfs2_recover_func()
will refuse to do anything during a withdraw.

However, before even getting to this point, gfs2_recover_func()
dereferences sdp->sd_jdesc->jd_inode.  This was a use-after-free before
commit 04133b607a78 ("gfs2: Prevent double iput for journal on error")
and is a NULL pointer dereference since then.

Simply get rid of self recovery to fix that.

## References
- https://git.kernel.org/stable/c/1a91ba12abef628b43cada87478328274d988e88
- https://git.kernel.org/stable/c/6784367b2f3cd7b89103de35764f37f152590dbd
- https://git.kernel.org/stable/c/69cf5699a402ee7ae1be53954dc2ae652c0a053c
- https://git.kernel.org/stable/c/6ebe17b359bead383581f729e43f591c1c36e159
- https://git.kernel.org/stable/c/97c94c7dbddc34d353c83b541b3decabf98d04af
- https://git.kernel.org/stable/c/deb016c1669002e48c431d6fd32ea1c20ef41756
- https://git.kernel.org/stable/c/f5426ffbec971a8f7346a57392d3a901bdee5a9b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38659.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38659
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
