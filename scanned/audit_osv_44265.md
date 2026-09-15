# [H] hwmon: (ltc4282) Fix reading the minimum alarm voltage

## Summary
Severity: High
Advisory: CVE-2026-80696
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-80696
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.9.0 <6.12.103, >=6.13.0 <6.18.44, >=6.19.0 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

hwmon: (ltc4282) Fix reading the minimum alarm voltage

Coverity reports an out-of-bounds access when reading the minimum alarm
voltage for the VGPIO channel. Add the missing return statement to fix
the problem.

## References
- https://git.kernel.org/stable/c/00feb1cce93dab948a299b69753d99c681d45a0b
- https://git.kernel.org/stable/c/08aee6d45eefc9e0b94c21bd442f47b21d64fa2c
- https://git.kernel.org/stable/c/338d655fe09b95a88788c6ac8b1651ca8db9ae51
- https://git.kernel.org/stable/c/a0668ac20feaa3fff9e0c0548556368dbbd2d439
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80696.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80696
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
