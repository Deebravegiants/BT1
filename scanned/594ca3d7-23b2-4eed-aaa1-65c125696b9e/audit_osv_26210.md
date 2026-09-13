# [M] pinctrl: nuvoton: wpcm450: fix out of bounds write

## Summary
Severity: Medium
Advisory: CVE-2023-52512
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-03-02
Source: https://osv.dev/vulnerability/CVE-2023-52512
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.18.0 <6.1.59, >=6.2.0 <6.5.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

pinctrl: nuvoton: wpcm450: fix out of bounds write

Write into 'pctrl->gpio_bank' happens before the check for GPIO index
validity, so out of bounds write may happen.

Found by Linux Verification Center (linuxtesting.org) with SVACE.

## References
- https://git.kernel.org/stable/c/6c18c386fd13dbb3ff31a1086dabb526780d9bda
- https://git.kernel.org/stable/c/87d315a34133edcb29c4cadbf196ec6c30dfd47b
- https://git.kernel.org/stable/c/c9d7cac0fd27c74dd368e80dc4b5d0f9f2e13cf8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52512.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52512
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
