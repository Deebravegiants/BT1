# [H] riscv: vector: Fix context save/restore with xtheadvector

## Summary
Severity: High
Advisory: CVE-2025-38435
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-07-25
Source: https://osv.dev/vulnerability/CVE-2025-38435
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.14.0 <6.15.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

riscv: vector: Fix context save/restore with xtheadvector

Previously only v0-v7 were correctly saved/restored,
and the context of v8-v31 are damanged.
Correctly save/restore v8-v31 to avoid breaking userspace.

## References
- https://git.kernel.org/stable/c/4262bd0d9cc704ea1365ac00afc1272400c2cbef
- https://git.kernel.org/stable/c/dd5ceea8d50e9e108a10d1e0d89fa2c9ff442ca2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38435.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38435
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
