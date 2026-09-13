# [H] crypto: stm32/cryp - call finalize with bh disabled

## Summary
Severity: High
Advisory: CVE-2024-47658
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-10-09
Source: https://osv.dev/vulnerability/CVE-2024-47658
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.16.0 <6.6.50, >=6.7.0 <6.10.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

crypto: stm32/cryp - call finalize with bh disabled

The finalize operation in interrupt mode produce a produces a spinlock
recursion warning. The reason is the fact that BH must be disabled
during this process.

## References
- https://git.kernel.org/stable/c/56ddb9aa3b324c2d9645b5a7343e46010cf3f6ce
- https://git.kernel.org/stable/c/5d734665cd5d93270731e0ff1dd673fec677f447
- https://git.kernel.org/stable/c/d93a2f86b0a998aa1f0870c85a2a60a0771ef89a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/47xxx/CVE-2024-47658.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-47658
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
