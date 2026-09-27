# [M] clk: mmp: pxa1908-apbc: Fix NULL vs IS_ERR() check

## Summary
Severity: Medium
Advisory: CVE-2024-58065
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-03-06
Source: https://osv.dev/vulnerability/CVE-2024-58065
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.13.0 <6.13.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

clk: mmp: pxa1908-apbc: Fix NULL vs IS_ERR() check

The devm_kzalloc() function returns NULL on error, not error pointers.
Fix the check.

## References
- https://git.kernel.org/stable/c/6628f7f88de5f65f01adef5a63c707cb49d0fddb
- https://git.kernel.org/stable/c/e5ca5d7b4d7c29246d957dc45d63610584ae3a54
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/58xxx/CVE-2024-58065.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-58065
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
