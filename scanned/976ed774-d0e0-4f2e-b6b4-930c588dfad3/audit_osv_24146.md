# [M] nfsd: Fix a memory leak in an error handling path

## Summary
Severity: Medium
Advisory: CVE-2022-50348
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-16
Source: https://osv.dev/vulnerability/CVE-2022-50348
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.4.0 <5.4.220, >=5.5.0 <5.10.150, >=5.11.0 <5.15.75, >=5.16.0 <5.19.17, >=5.20.0 <6.0.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

nfsd: Fix a memory leak in an error handling path

If this memdup_user() call fails, the memory allocated in a previous call
a few lines above should be freed. Otherwise it leaks.

## References
- https://git.kernel.org/stable/c/733dd17158f96aaa25408dc39bbb2738fda9300e
- https://git.kernel.org/stable/c/acc393aecda05bf64ed13b732931462e07a1bf08
- https://git.kernel.org/stable/c/aed8816305575b38dcc77feb6f1bc1d0ed32f5b8
- https://git.kernel.org/stable/c/cc3bca2110ac85cd964da997ef83d84cab0d49fb
- https://git.kernel.org/stable/c/e060c4b9f33c1fca74df26d57a98e784295327e6
- https://git.kernel.org/stable/c/fd1ef88049de09bc70d60b549992524cfc0e66ff
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50348.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50348
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
