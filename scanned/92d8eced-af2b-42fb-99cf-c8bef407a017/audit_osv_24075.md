# [H] net: lantiq_xrx200: restore buffer if memory allocation failed

## Summary
Severity: High
Advisory: CVE-2022-49997
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-06-18
Source: https://osv.dev/vulnerability/CVE-2022-49997
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.13.0 <5.19.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: lantiq_xrx200: restore buffer if memory allocation failed

In a situation where memory allocation fails, an invalid buffer address
is stored. When this descriptor is used again, the system panics in the
build_skb() function when accessing memory.

## References
- https://git.kernel.org/stable/c/3ef2786e32d93e562cd40601248a14ae090de873
- https://git.kernel.org/stable/c/c9c3b1775f80fa21f5bff874027d2ccb10f5d90c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49997.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49997
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
