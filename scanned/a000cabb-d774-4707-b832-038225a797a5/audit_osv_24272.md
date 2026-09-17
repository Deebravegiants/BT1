# [H] fsi: occ: Prevent use after free

## Summary
Severity: High
Advisory: CVE-2022-50785
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-30
Source: https://osv.dev/vulnerability/CVE-2022-50785
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.16.0 <5.19.17, >=5.20.0 <6.0.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

fsi: occ: Prevent use after free

Use get_device and put_device in the open and close functions to
make sure the device doesn't get freed while a file descriptor is
open.
Also, lock around the freeing of the device buffer and check the
buffer before using it in the submit function.

## References
- https://git.kernel.org/stable/c/1d5ad0a874ddfcee9f932f54b1d34cbe8b9ddcfe
- https://git.kernel.org/stable/c/3593e8efc9f0dac6be70bd5c964eadaa86bf2713
- https://git.kernel.org/stable/c/d3e1e24604031b0d83b6c2d38f54eeea265cfcc0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50785.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50785
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
