# [M] EDAC/bluefield: Fix potential integer overflow

## Summary
Severity: Medium
Advisory: CVE-2024-53161
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-12-24
Source: https://osv.dev/vulnerability/CVE-2024-53161
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.4.0 <5.4.287, >=5.5.0 <5.10.231, >=5.11.0 <5.15.174, >=5.16.0 <6.1.120, >=6.2.0 <6.6.64, >=6.7.0 <6.11.11, >=6.12.0 <6.12.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

EDAC/bluefield: Fix potential integer overflow

The 64-bit argument for the "get DIMM info" SMC call consists of mem_ctrl_idx
left-shifted 16 bits and OR-ed with DIMM index.  With mem_ctrl_idx defined as
32-bits wide the left-shift operation truncates the upper 16 bits of
information during the calculation of the SMC argument.

The mem_ctrl_idx stack variable must be defined as 64-bits wide to prevent any
potential integer overflow, i.e. loss of data from upper 16 bits.

## References
- https://git.kernel.org/stable/c/000930193fe5eb79ce5563ee2e9ddb0c6e4e1bb5
- https://git.kernel.org/stable/c/1fe774a93b46bb029b8f6fa9d1f25affa53f06c6
- https://git.kernel.org/stable/c/4ad7033de109d0fec99086f352f58a3412e378b8
- https://git.kernel.org/stable/c/578ca89b04680145d41011e7cec8806fefbb59e7
- https://git.kernel.org/stable/c/8cc31cfa36ff37aff399b72faa2ded58110112ae
- https://git.kernel.org/stable/c/ac6ebb9edcdb7077e841862c402697c4c48a7c0a
- https://git.kernel.org/stable/c/e0269ea7a628fdeddd65b92fe29c09655dbb80b9
- https://git.kernel.org/stable/c/fdb90006184aa84c7b4e09144ed0936d4e1891a7
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53161.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53161
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
