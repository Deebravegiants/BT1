# [H] s390/uv: Don't call folio_wait_writeback() without a folio reference

## Summary
Severity: High
Advisory: CVE-2024-43832
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-08-17
Source: https://osv.dev/vulnerability/CVE-2024-43832
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.7.0 <6.1.103, >=6.2.0 <6.6.44, >=6.7.0 <6.10.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

s390/uv: Don't call folio_wait_writeback() without a folio reference

folio_wait_writeback() requires that no spinlocks are held and that
a folio reference is held, as documented. After we dropped the PTL, the
folio could get freed concurrently. So grab a temporary reference.

## References
- https://git.kernel.org/stable/c/1a1eb2f3fc453dcd52726d13e863938561489cb7
- https://git.kernel.org/stable/c/3f29f6537f54d74e64bac0a390fb2e26da25800d
- https://git.kernel.org/stable/c/8736604ef53359a718c246087cd21dcec232d2fb
- https://git.kernel.org/stable/c/b21aba72aadd94bdac275deab021fc84d6c72b16
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/43xxx/CVE-2024-43832.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-43832
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
