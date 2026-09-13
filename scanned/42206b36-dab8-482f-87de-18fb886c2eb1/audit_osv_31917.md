# [M] pinctrl: nuvoton: npcm8xx: Add NULL check in npcm8xx_gpio_fw

## Summary
Severity: Medium
Advisory: CVE-2025-21982
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-04-01
Source: https://osv.dev/vulnerability/CVE-2025-21982
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.7.0 <6.12.20, >=6.13.0 <6.13.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

pinctrl: nuvoton: npcm8xx: Add NULL check in npcm8xx_gpio_fw

devm_kasprintf() calls can return null pointers on failure.
But the return values were not checked in npcm8xx_gpio_fw().
Add NULL check in npcm8xx_gpio_fw(), to handle kernel NULL
pointer dereference error.

## References
- https://git.kernel.org/stable/c/6a08a86e5aff8e65368ccd463348fdda26100821
- https://git.kernel.org/stable/c/a585f6ea42ec259a9a57e3e2580fa527c92187d0
- https://git.kernel.org/stable/c/acf40ab42799e4ae1397ee6f5c5941092d66f999
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21982.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21982
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
