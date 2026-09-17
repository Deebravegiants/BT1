# [M] HID: winwing: Add NULL check in winwing_init_led()

## Summary
Severity: Medium
Advisory: CVE-2024-58021
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-27
Source: https://osv.dev/vulnerability/CVE-2024-58021
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.10.0 <6.12.16, >=6.13.0 <6.13.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

HID: winwing: Add NULL check in winwing_init_led()

devm_kasprintf() can return a NULL pointer on failure,but this
returned value in winwing_init_led() is not checked.
Add NULL check in winwing_init_led(), to handle kernel NULL
pointer dereference error.

## References
- https://git.kernel.org/stable/c/4001f6f79183b8868d80dd2036dfb4ea3d325e8f
- https://git.kernel.org/stable/c/45ab5166a82d038c898985b0ad43ead69c1f9573
- https://git.kernel.org/stable/c/b99dbdee8a89c44d03ae9830ab19f31e124a3f32
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/58xxx/CVE-2024-58021.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-58021
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
