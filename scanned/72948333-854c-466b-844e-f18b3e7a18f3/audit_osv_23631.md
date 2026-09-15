# [H] crypto: ccree - Fix use after free in cc_cipher_exit()

## Summary
Severity: High
Advisory: CVE-2022-49258
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49258
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.17.0 <5.10.110, >=5.11.0 <5.15.33, >=5.16.0 <5.16.19, >=5.17.0 <5.17.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

crypto: ccree - Fix use after free in cc_cipher_exit()

kfree_sensitive(ctx_p->user.key) will free the ctx_p->user.key. But
ctx_p->user.key is still used in the next line, which will lead to a
use after free.

We can call kfree_sensitive() after dev_dbg() to avoid the uaf.

## References
- https://git.kernel.org/stable/c/25c358efee5153dfd240d4e0d3169d5bebe9cacd
- https://git.kernel.org/stable/c/335bf1fc74f775a8255257aa3e33763f2257b676
- https://git.kernel.org/stable/c/3d950c34074ed74d2713c3856ba01264523289e6
- https://git.kernel.org/stable/c/c93017c8d5ebf55a4e453ac7c84cc84cf92ab570
- https://git.kernel.org/stable/c/cffb5382bd8d3cf21b874ab5b84bf7618932286b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49258.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49258
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
