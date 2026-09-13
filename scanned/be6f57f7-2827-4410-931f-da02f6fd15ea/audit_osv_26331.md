# [H] drm/radeon: possible buffer overflow

## Summary
Severity: High
Advisory: CVE-2023-52867
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2023-52867
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.13.0 <4.14.330, >=4.15.0 <4.19.299, >=4.20.0 <5.4.261, >=5.5.0 <5.10.201, >=5.11.0 <5.15.139, >=5.16.0 <6.1.63, >=6.2.0 <6.5.12, >=6.6.0 <6.6.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/radeon: possible buffer overflow

Buffer 'afmt_status' of size 6 could overflow, since index 'afmt_idx' is
checked after access.

## References
- https://git.kernel.org/stable/c/112d4b02d94bf9fa4f1d3376587878400dd74783
- https://git.kernel.org/stable/c/19534a7a225f1bf2da70a9a90d41d0215f8f6b45
- https://git.kernel.org/stable/c/341e79f8aec6af6b0061b8171d77b085835c6a58
- https://git.kernel.org/stable/c/347f025a02b3a5d715a0b471fc3b1439c338ad94
- https://git.kernel.org/stable/c/7b063c93bece827fde237fae1c101bceeee4e896
- https://git.kernel.org/stable/c/caaa74541459c4c9e2c10046cf66ad2890483d0f
- https://git.kernel.org/stable/c/d9b4fa249deaae1145d6fc2b64dae718e5c7a855
- https://git.kernel.org/stable/c/dd05484f99d16715a88eedfca363828ef9a4c2d4
- https://git.kernel.org/stable/c/ddc42881f170f1f518496f5a70447501335fc783
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52867.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52867
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
