# [H] hwmon: (nct6775) Fix access to temperature configuration registers

## Summary
Severity: High
Advisory: CVE-2024-26730
Ecosystem: Linux
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:H)
Published: 2024-04-03
Source: https://osv.dev/vulnerability/CVE-2024-26730
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.6.0 <6.6.19, >=6.7.0 <6.7.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

hwmon: (nct6775) Fix access to temperature configuration registers

The number of temperature configuration registers does
not always match the total number of temperature registers.
This can result in access errors reported if KASAN is enabled.

BUG: KASAN: global-out-of-bounds in nct6775_probe+0x5654/0x6fe9 nct6775_core

## References
- https://git.kernel.org/stable/c/745aa03c513f1ba12cb98495467676f7acf3fffd
- https://git.kernel.org/stable/c/c196387820c9214c5ceaff56d77303c82514b8b1
- https://git.kernel.org/stable/c/d56e460e19ea8382f813eb489730248ec8d7eb73
- https://git.kernel.org/stable/c/f006c45a3ea424f8f6c8e4b9283bc245ce2a4d0f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26730.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26730
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
