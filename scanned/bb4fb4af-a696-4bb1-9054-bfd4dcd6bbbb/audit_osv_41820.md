# [H] usb: dwc2: Fix use after free in debug code

## Summary
Severity: High
Advisory: CVE-2026-63927
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-63927
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.10.0 <5.10.259, >=5.11.0 <5.15.210, >=5.16.0 <6.1.176, >=6.2.0 <6.6.143, >=6.7.0 <6.12.93, >=6.13.0 <6.18.35, >=6.19.0 <7.0.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

usb: dwc2: Fix use after free in debug code

We're not allowed to dereference "urb" after calling
usb_hcd_giveback_urb() so save the urb->status ahead of time.

## References
- https://git.kernel.org/stable/c/0584af4fe40fa5e254a05d69ce658746de641708
- https://git.kernel.org/stable/c/63b0dafa676aad4d0c3f01a61ad8e2990907660c
- https://git.kernel.org/stable/c/6d0b79d1d1118145e48a68192b6d733e39387053
- https://git.kernel.org/stable/c/84ea928ed584756e59c6ac09736f12d1db95ded0
- https://git.kernel.org/stable/c/9ea06a3fbf9f16e0d98c52cb3b99642be15ec281
- https://git.kernel.org/stable/c/9fe1d84f7e2cf33634e8afb7f4b7f8de182dd913
- https://git.kernel.org/stable/c/a15eeeceb94cbc04edef395e4d777ff554bdc27d
- https://git.kernel.org/stable/c/d5fc183ed614aeba6779cc992325be560f9a4451
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63927.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63927
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
