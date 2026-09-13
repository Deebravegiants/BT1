# [H] xfs: propagate errors from xfs_rtginode_load

## Summary
Severity: High
Advisory: CVE-2026-80538
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H)
Published: 2026-08-26
Source: https://osv.dev/vulnerability/CVE-2026-80538
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.13.0 <6.18.46, >=6.19.0 <7.1.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

xfs: propagate errors from xfs_rtginode_load

xfs_rtginode_ensure() treats every xfs_rtginode_load() error other than
-ENOENT as success.  This can leave the realtime group inode unset after an
I/O, allocation, or corruption error.  Growfs then continues as though the
inode had been loaded.

Only -ENOENT means that the inode needs to be created.  Return all other
errors to the growfs caller.

## References
- https://git.kernel.org/stable/c/61c5165f02deb2eed9b6b539bb279e6629fee652
- https://git.kernel.org/stable/c/b7e53968cb8882c2d276429ea8550848a4940874
- https://git.kernel.org/stable/c/ec19cea4ef1ce9d6e2e3f7e9e7bf88ede31176e7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80538.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80538
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
