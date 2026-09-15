# [H] Revert "arm64: zynqmp: Add an OP-TEE node to the device tree"

## Summary
Severity: High
Advisory: CVE-2025-71300
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-08
Source: https://osv.dev/vulnerability/CVE-2025-71300
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.9.0 <6.12.75, >=6.13.0 <6.18.16, >=6.19.0 <6.19.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

Revert "arm64: zynqmp: Add an OP-TEE node to the device tree"

This reverts commit 06d22ed6b6635b17551f386b50bb5aaff9b75fbe.

OP-TEE logic in U-Boot automatically injects a reserved-memory
node along with optee firmware node to kernel device tree.
The injection logic is dependent on that there is no manually
defined optee node. Having the node in zynqmp.dtsi effectively
breaks OP-TEE's insertion of the reserved-memory node, causing
memory access violations during runtime.

## References
- https://git.kernel.org/stable/c/2a833c730d4e8d1cc10953270ce0f3a156145d81
- https://git.kernel.org/stable/c/3983ef126e439900bbf419724a9759863c146660
- https://git.kernel.org/stable/c/c197179990124f991fca220d97fac56779a02c6d
- https://git.kernel.org/stable/c/eece81eeda10eb42c687399fb5aa69977ae15664
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/71xxx/CVE-2025-71300.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-71300
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
