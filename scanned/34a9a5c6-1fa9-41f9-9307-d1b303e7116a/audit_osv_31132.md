# [M] mailbox: th1520: Fix a NULL vs IS_ERR() bug

## Summary
Severity: Medium
Advisory: CVE-2024-58022
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-27
Source: https://osv.dev/vulnerability/CVE-2024-58022
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.13.0 <6.13.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

mailbox: th1520: Fix a NULL vs IS_ERR() bug

The devm_ioremap() function doesn't return error pointers, it returns
NULL.  Update the error checking to match.

## References
- https://git.kernel.org/stable/c/d0f98e14c010bcf27898b635a54c1994ac4110a8
- https://git.kernel.org/stable/c/ecbde88e544ff016fa08bbf2156dc431bb123e9b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/58xxx/CVE-2024-58022.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-58022
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
