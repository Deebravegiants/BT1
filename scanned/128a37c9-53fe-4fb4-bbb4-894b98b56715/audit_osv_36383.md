# [H] accel/amdxdna: Fix out-of-bounds memset in command slot handling

## Summary
Severity: High
Advisory: CVE-2026-23288
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-03-25
Source: https://osv.dev/vulnerability/CVE-2026-23288
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.19.4 <6.19.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

accel/amdxdna: Fix out-of-bounds memset in command slot handling

The remaining space in a command slot may be smaller than the size of
the command header. Clearing the command header with memset() before
verifying the available slot space can result in an out-of-bounds write
and memory corruption.

Fix this by moving the memset() call after the size validation.

## References
- https://git.kernel.org/stable/c/1110a949675ebd56b3f0286e664ea543f745801c
- https://git.kernel.org/stable/c/cca770d710d5e03bc814af585cd6975eb6d74074
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23288.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-23288
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
