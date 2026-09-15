# [H] powerpc/uaccess: correct check for CONFIG_PPC_E500 in mask_user_address()

## Summary
Severity: High
Advisory: CVE-2026-68473
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-68473
Type: osv

## Affected
- Linux: `Kernel` — affected >=7.0.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

powerpc/uaccess: correct check for CONFIG_PPC_E500 in mask_user_address()

mask_user_address() incorrectly checks for CONFIG_E500 instead of
CONFIG_PPC_E500, causing mask_user_address_isel() to not be used on
E500 hardware. Fix the check to use the correct name.

## References
- https://git.kernel.org/stable/c/d5c234774a82f27b594f70c15fc45ce3648e4295
- https://git.kernel.org/stable/c/d610d3ab18197d87618da11ec5fe8b3cebf32208
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68473.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68473
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
