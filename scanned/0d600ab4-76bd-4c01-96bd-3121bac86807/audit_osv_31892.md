# [H] ksmbd: fix out-of-bounds in parse_sec_desc()

## Summary
Severity: High
Advisory: CVE-2025-21946
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-04-01
Source: https://osv.dev/vulnerability/CVE-2025-21946
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <6.1.160, >=6.2.0 <6.6.83, >=6.7.0 <6.12.19, >=6.13.0 <6.13.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: fix out-of-bounds in parse_sec_desc()

If osidoffset, gsidoffset and dacloffset could be greater than smb_ntsd
struct size. If it is smaller, It could cause slab-out-of-bounds.
And when validating sid, It need to check it included subauth array size.

## References
- https://git.kernel.org/stable/c/159d059cbcb0e6d0e7a7b34af3862ba09a6b22d1
- https://git.kernel.org/stable/c/6a9831180d0b23b5c97e2bd841aefc8f82900172
- https://git.kernel.org/stable/c/c1569dbbe2d43041be9f3fef7ca08bec3b66ad1b
- https://git.kernel.org/stable/c/d6e13e19063db24f94b690159d0633aaf72a0f03
- https://git.kernel.org/stable/c/f4ee19528664777af8b842f8f001be98345aa973
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21946.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21946
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
