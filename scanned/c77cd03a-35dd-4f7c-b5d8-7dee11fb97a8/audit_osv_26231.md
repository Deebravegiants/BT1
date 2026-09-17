# [H] f2fs: fix to tag gcing flag on page during block migration

## Summary
Severity: High
Advisory: CVE-2023-52588
Ecosystem: Linux
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:H)
Published: 2024-03-06
Source: https://osv.dev/vulnerability/CVE-2023-52588
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.8.0 <5.15.149, >=5.16.0 <6.1.77, >=6.2.0 <6.6.16, >=6.7.0 <6.7.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

f2fs: fix to tag gcing flag on page during block migration

It needs to add missing gcing flag on page during block migration,
in order to garantee migrated data be persisted during checkpoint,
otherwise out-of-order persistency between data and node may cause
data corruption after SPOR.

Similar issue was fixed by commit 2d1fe8a86bf5 ("f2fs: fix to tag
gcing flag on page during file defragment").

## References
- https://git.kernel.org/stable/c/417b8a91f4e8831cadaf85c3f15c6991c1f54dde
- https://git.kernel.org/stable/c/4961acdd65c956e97c1a000c82d91a8c1cdbe44b
- https://git.kernel.org/stable/c/7c972c89457511007dfc933814c06786905e515c
- https://git.kernel.org/stable/c/7ea0f29d9fd84905051be020c0df7d557e286136
- https://git.kernel.org/stable/c/b8094c0f1aae329b1c60a275a780d6c2c9ff7aa3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52588.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52588
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
