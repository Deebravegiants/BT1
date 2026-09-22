# [H] fuse: re-lock request before returning from fuse_ref_folio()

## Summary
Severity: High
Advisory: CVE-2026-64266
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/CVE-2026-64266
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.35 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.96, >=6.13.0 <6.18.39, >=6.19.0 <7.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

fuse: re-lock request before returning from fuse_ref_folio()

fuse_ref_folio() unlocks the request but does not re-lock it before
returning. fuse_chan_abort() can end the request and the async end
callback (eg fuse_writepage_free()) can free the args while the
subsequent copy chain logic after fuse_ref_folio() accesses them,
leading to use-after-free issues.

Fix this by locking the request in fuse_ref_folio() before returning.

## References
- https://git.kernel.org/stable/c/0e4a5a000123d81234e27a2f8187688cf608f755
- https://git.kernel.org/stable/c/1ca605cfa59377f0143fb35b5b01360f37d1b7c4
- https://git.kernel.org/stable/c/1f9156714592356b4fda57beac7eab9c2a462dd3
- https://git.kernel.org/stable/c/5630da218a45ba80f0aba0846cbe8aa655da122b
- https://git.kernel.org/stable/c/65a1c2551f7e16085acbb54aedde1feaa559ba7a
- https://git.kernel.org/stable/c/b5befa80fdbe287a98480effed9564712924add5
- https://git.kernel.org/stable/c/be353caffa8640f5e25fb3714ce8b0cef5e410e5
- https://git.kernel.org/stable/c/e6aa539720c3d8def69683ed0c07cf9faea4e8be
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64266.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64266
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
