# [H] vt: Clear selection before changing the font

## Summary
Severity: High
Advisory: CVE-2022-49948
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-06-18
Source: https://osv.dev/vulnerability/CVE-2022-49948
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.9.0 <4.9.328, >=4.10.0 <4.14.293, >=4.15.0 <4.19.258, >=4.20.0 <5.4.213, >=5.5.0 <5.10.142, >=5.11.0 <5.15.66, >=5.16.0 <5.19.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

vt: Clear selection before changing the font

When changing the console font with ioctl(KDFONTOP) the new font size
can be bigger than the previous font. A previous selection may thus now
be outside of the new screen size and thus trigger out-of-bounds
accesses to graphics memory if the selection is removed in
vc_do_resize().

Prevent such out-of-memory accesses by dropping the selection before the
various con_font_set() console handlers are called.

## References
- https://git.kernel.org/stable/c/1cf1930369c9dc428d827b60260c53271bff3285
- https://git.kernel.org/stable/c/2535431ae967ad17585513649625fea7db28d4db
- https://git.kernel.org/stable/c/566f9c9f89337792070b5a6062dff448b3e7977f
- https://git.kernel.org/stable/c/989201bb8c00b222235aff04e6200230d29dc7bb
- https://git.kernel.org/stable/c/c555cf04684fde39b5b0dd9fd80730030ee10c4a
- https://git.kernel.org/stable/c/c904fe03c4bd1f356a58797d39e2a5d0ca15cefc
- https://git.kernel.org/stable/c/e9ba4611ddf676194385506222cce7b0844e708e
- https://git.kernel.org/stable/c/f74b4a41c5d7c9522469917e3072e55d435efd9e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49948.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49948
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
