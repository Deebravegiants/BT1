# [H] usb: usbtmc: Flush anchored URBs in usbtmc_release

## Summary
Severity: High
Advisory: CVE-2026-31758
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-01
Source: https://osv.dev/vulnerability/CVE-2026-31758
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.19.0 <5.10.253, >=5.11.0 <5.15.203, >=5.16.0 <6.1.168, >=6.2.0 <6.6.134, >=6.7.0 <6.12.81, >=6.13.0 <6.18.22, >=6.19.0 <6.19.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

usb: usbtmc: Flush anchored URBs in usbtmc_release

When calling usbtmc_release, pending anchored URBs must be flushed or
killed to prevent use-after-free errors (e.g. in the HCD giveback
path). Call usbtmc_draw_down() to allow anchored URBs to be completed.

## References
- https://git.kernel.org/stable/c/7fa8f61bab3fb75b5deba8a0f3abb74dc5068d9f
- https://git.kernel.org/stable/c/8a768552f7a8276fb9e01d49773d2094ace7c8f1
- https://git.kernel.org/stable/c/959ef329071136e4335b54822fe2f607659b4569
- https://git.kernel.org/stable/c/95e09b07e50290254b28b8395509473104518f8c
- https://git.kernel.org/stable/c/977b632db51d231dec0bc571089a5c2402674139
- https://git.kernel.org/stable/c/d13318dec0c1e0e2ac16f8ecbd522db14cea4bb1
- https://git.kernel.org/stable/c/d40198de50232e04c14c6e2092e896766c95ea48
- https://git.kernel.org/stable/c/e189d443767f7cd390c52f2e122e1fc41c7562d6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31758.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31758
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
