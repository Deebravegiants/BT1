# [H] iio: adc: axp20x_adc: Add missing sentinel to AXP717 ADC channel maps

## Summary
Severity: High
Advisory: CVE-2025-38547
Ecosystem: Linux
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:H)
Published: 2025-08-16
Source: https://osv.dev/vulnerability/CVE-2025-38547
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.12.0 <6.12.40, >=6.13.0 <6.15.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

iio: adc: axp20x_adc: Add missing sentinel to AXP717 ADC channel maps

The AXP717 ADC channel maps is missing a sentinel entry at the end. This
causes a KASAN warning.

Add the missing sentinel entry.

## References
- https://git.kernel.org/stable/c/086a76474121bf2351438e311376ec67b410b2ea
- https://git.kernel.org/stable/c/0c0c01c88bb69951539539d2001e67f0c613001f
- https://git.kernel.org/stable/c/3281ddcea6429f7bc1fdb39d407752dd1371aba9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38547.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38547
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
