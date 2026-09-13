# [M] ASoC: imx-card: Add NULL check in imx_card_probe()

## Summary
Severity: Medium
Advisory: CVE-2025-22066
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-04-16
Source: https://osv.dev/vulnerability/CVE-2025-22066
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.14.0 <5.15.180, >=5.16.0 <6.1.134, >=6.2.0 <6.6.87, >=6.7.0 <6.12.23, >=6.13.0 <6.13.11, >=6.14.0 <6.14.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

ASoC: imx-card: Add NULL check in imx_card_probe()

devm_kasprintf() returns NULL when memory allocation fails. Currently,
imx_card_probe() does not check for this case, which results in a NULL
pointer dereference.

Add NULL check after devm_kasprintf() to prevent this issue.

## References
- https://git.kernel.org/stable/c/018e6cf2503e60087747b0ebc190e18b3640766f
- https://git.kernel.org/stable/c/38253922a89a742e7e622f626b41c64388367361
- https://git.kernel.org/stable/c/4d8458e48ff135bddc402ad79821dc058ea163d0
- https://git.kernel.org/stable/c/93d34608fd162f725172e780b1c60cc93a920719
- https://git.kernel.org/stable/c/b01700e08be99e3842570142ec5973ccd7e73eaf
- https://git.kernel.org/stable/c/dd2bbb9564d0d24a2643ad90008a79840368c4b4
- https://git.kernel.org/stable/c/e283a5bf4337a7300ac5e6ae363cc8b242a0b4b7
- https://lists.debian.org/debian-lts-announce/2025/05/msg00045.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/22xxx/CVE-2025-22066.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-22066
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
