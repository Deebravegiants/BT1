# [M] usbnet: fix memory leak in error case

## Summary
Severity: Medium
Advisory: CVE-2022-49657
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49657
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.8.0 <4.9.323, >=4.10.0 <4.14.288, >=4.15.0 <4.19.252, >=4.20.0 <5.4.205, >=5.5.0 <5.10.130, >=5.11.0 <5.15.54, >=5.16.0 <5.18.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

usbnet: fix memory leak in error case

usbnet_write_cmd_async() mixed up which buffers
need to be freed in which error case.

v2: add Fixes tag
v3: fix uninitialized buf pointer

## References
- https://git.kernel.org/stable/c/0085da9df3dced730027923a6b48f58e9016af91
- https://git.kernel.org/stable/c/04894ab34faf40ab72a8a5ab5b404bb0606bbbff
- https://git.kernel.org/stable/c/3eed421ca5c809da93456f69203d164d5220be3d
- https://git.kernel.org/stable/c/5269209f54dd8dfd15f9383f3a3a1fe8370764f8
- https://git.kernel.org/stable/c/b55a21b764c1e182014630fa5486d717484ac58f
- https://git.kernel.org/stable/c/d5165e657987ff4ba0ace896d4376a3718a9fbc3
- https://git.kernel.org/stable/c/db89582ff330556188da856e01382ccbf3a5e706
- https://git.kernel.org/stable/c/e7b4f69946a38209b4a4f660bf0e4cbed94f9b4b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49657.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49657
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
