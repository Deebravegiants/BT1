# [H] virtiofs: fix UAF on submount umount

## Summary
Severity: High
Advisory: CVE-2026-53381
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-53381
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.10.260, >=5.11.0 <5.15.211, >=5.16.0 <6.1.177, >=6.2.0 <6.6.144, >=6.7.0 <6.12.95, >=6.13.0 <6.18.37, >=6.18.0 <7.0.14, >=6.19.0 <7.1.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

virtiofs: fix UAF on submount umount

iput() called from fuse_release_end() can Oops if the super block has
already been destroyed.  Normally this is prevented by waiting for
num_waiting to go down to zero before commencing with super block shutdown.

This only works, however, for the last submount instance, as the wait
counter is per connection, not per superblock.

Revert to using synchronous release requests for the auto_submounts case,
which is virtiofs only at this time.

## References
- https://git.kernel.org/stable/c/06b41351779e9289e8785694ade9042ae85e41ea
- https://git.kernel.org/stable/c/0b809199ff87c44487e516a725dd4be2185712ce
- https://git.kernel.org/stable/c/1cc0e3a0c6499aaaa2f21a4fcbba388486afb25e
- https://git.kernel.org/stable/c/2181a09ba980f142650fb053666350ead4471cfe
- https://git.kernel.org/stable/c/2abfd3ffbd9452f72535d96ff3982b3ab1f8f2f9
- https://git.kernel.org/stable/c/39a2b95e008665c14f84e50ed411d898df7cd11b
- https://git.kernel.org/stable/c/607a1d4c42f649e6197567c0448fd9ebb316cd42
- https://git.kernel.org/stable/c/97c4691653d145dcc699eca5d3aba3219a520f1f
- https://git.kernel.org/stable/c/e09412a714bcd49375198427bb4aa005037a9d6f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53381.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53381
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
