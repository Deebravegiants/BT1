# [H] Input: psxpad-spi - set driver data before use

## Summary
Severity: High
Advisory: CVE-2026-80752
Ecosystem: Linux
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-09-03
Source: https://osv.dev/vulnerability/CVE-2026-80752
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.12.0 <5.10.266, >=5.11.0 <5.15.217, >=5.16.0 <6.1.184, >=6.2.0 <6.6.153, >=6.7.0 <6.12.105, >=6.13.0 <6.18.46, >=6.19.0 <7.1.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

Input: psxpad-spi - set driver data before use

psxpad_spi_suspend() retrieves the controller state with
spi_get_drvdata(), but probe never stores it, so suspend dereferences a
NULL pointer. Store it during probe.

## References
- https://git.kernel.org/stable/c/1bba6bd6861b1e0c8ecf20cd1892f0d3877c02a2
- https://git.kernel.org/stable/c/1edcb7ffee7ac4dc35cbe5bbd0e27bac3614ebe4
- https://git.kernel.org/stable/c/62e25677d1440085381b047ec4984be9b6793759
- https://git.kernel.org/stable/c/732f38c36059e68ba3b4b89c56911d777fd3185c
- https://git.kernel.org/stable/c/86531cdfb3a03213e2569deed5195412a4e3f7ee
- https://git.kernel.org/stable/c/8d622c58205adbc8af19864e277386528b671345
- https://git.kernel.org/stable/c/da6b8b05db0cf43e0cc198431fa8ee9739b3b817
- https://git.kernel.org/stable/c/e980066e434a9c74ff1665ed9140427e95b0ee7c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80752.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80752
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
