# [H] fs: hfsplus: remove WARN_ON() from hfsplus_cat_{read,write}_inode()

## Summary
Severity: High
Advisory: CVE-2023-53683
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-07
Source: https://osv.dev/vulnerability/CVE-2023-53683
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <4.14.316, >=4.15.0 <4.19.284, >=4.20.0 <5.4.244, >=5.5.0 <5.10.181, >=5.11.0 <5.15.113, >=5.16.0 <6.3.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

fs: hfsplus: remove WARN_ON() from hfsplus_cat_{read,write}_inode()

syzbot is hitting WARN_ON() in hfsplus_cat_{read,write}_inode(), for
crafted filesystem image can contain bogus length. There conditions are
not kernel bugs that can justify kernel to panic.

## References
- https://git.kernel.org/stable/c/37cab61a52d6f42b2d961c51bcf369f09e235fb5
- https://git.kernel.org/stable/c/3a9d68d84b2e41ba3f2a727b36f035fad6800492
- https://git.kernel.org/stable/c/48960a503fcec76d3f72347b7e679dda08ca43be
- https://git.kernel.org/stable/c/61af77acd039ffd221bf7adf0dc95d0a4d377505
- https://git.kernel.org/stable/c/81b21c0f0138ff5a499eafc3eb0578ad2a99622c
- https://git.kernel.org/stable/c/a75d9211a07fed513c08c5d4861c4a36ac6a74fe
- https://git.kernel.org/stable/c/c074913b12db3632b11588b31bbfb0fa80a0a1c9
- https://git.kernel.org/stable/c/c8daee66585897a4c90d937c91e762100237bff9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53683.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53683
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
