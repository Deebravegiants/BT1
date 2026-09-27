# [H] wifi: ath12k: fix the error handler of rfkill config

## Summary
Severity: High
Advisory: CVE-2023-52688
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-17
Source: https://osv.dev/vulnerability/CVE-2023-52688
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.7.0 <6.7.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: ath12k: fix the error handler of rfkill config

When the core rfkill config throws error, it should free the
allocated resources. Currently it is not freeing the core pdev
create resources. Avoid this issue by calling the core pdev
destroy in the error handler of core rfkill config.

Found this issue in the code review and it is compile tested only.

## References
- https://git.kernel.org/stable/c/898d8b3e1414cd900492ee6a0b582f8095ba4a1a
- https://git.kernel.org/stable/c/b4e593a7a22fa3c7d0550ef51c90b5c21f790aa8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52688.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52688
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
