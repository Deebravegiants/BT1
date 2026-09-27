# [M] drm/amd: Fix UBSAN array-index-out-of-bounds for Polaris and Tonga

## Summary
Severity: Medium
Advisory: CVE-2023-52819
Ecosystem: Linux
CVSS: 6.6 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2023-52819
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.5.0 <4.14.331, >=4.15.0 <4.19.300, >=4.20.0 <5.4.262, >=5.5.0 <5.10.202, >=5.11.0 <5.15.140, >=5.16.0 <6.1.64, >=6.2.0 <6.5.13, >=6.6.0 <6.6.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amd: Fix UBSAN array-index-out-of-bounds for Polaris and Tonga

For pptable structs that use flexible array sizes, use flexible arrays.

## References
- https://git.kernel.org/stable/c/0f0e59075b5c22f1e871fbd508d6e4f495048356
- https://git.kernel.org/stable/c/60a00dfc7c5deafd1dd393beaf53224f7256dad6
- https://git.kernel.org/stable/c/7c68283f3166221af3df5791f0e13d3137a72216
- https://git.kernel.org/stable/c/8c1dbddbfcb051e82cea0c197c620f9dcdc38e92
- https://git.kernel.org/stable/c/a237675aa1e62bbfaa341c535331c8656a508fa1
- https://git.kernel.org/stable/c/a63fd579e7b1c3a9ebd6e6c494d49b1b6cf5515e
- https://git.kernel.org/stable/c/b3b8b7c040cf069da7afe11c5bd73b870b8f3d18
- https://git.kernel.org/stable/c/d0725232da777840703f5f1e22f2e3081d712aa4
- https://git.kernel.org/stable/c/d50a56749e5afdc63491b88f5153c1aae00d4679
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52819.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52819
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
