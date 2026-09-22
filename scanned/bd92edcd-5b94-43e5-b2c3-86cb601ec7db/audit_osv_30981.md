# [H] CVE-2024-57258

## Summary
Severity: High
Advisory: CVE-2024-57258
CVSS: 7.1 (CVSS:3.1/AV:P/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2025-02-18
Source: https://osv.dev/vulnerability/CVE-2024-57258
Type: osv

## Details
Integer overflows in memory allocation in Das U-Boot before 2025.01-rc1 occur for a crafted squashfs filesystem via sbrk, via request2size, or because ptrdiff_t is mishandled on x86_64.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-577017.html
- https://lists.debian.org/debian-lts-announce/2025/05/msg00001.html
- https://source.denx.de/u-boot/u-boot/-/commit/0a10b49206a29b4aa2f80233a3e53ca0466bb0b3
- https://source.denx.de/u-boot/u-boot/-/commit/8642b2178d2c4002c99a0b69a845a48f2ae2706f
- https://source.denx.de/u-boot/u-boot/-/commit/c17b2a05dd50a3ba437e6373093a0d6a359cdee0
- https://www.openwall.com/lists/oss-security/2025/02/17/2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/57xxx/CVE-2024-57258.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-57258
