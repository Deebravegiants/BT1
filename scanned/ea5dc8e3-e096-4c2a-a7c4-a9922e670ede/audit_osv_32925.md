# [H] eth: fbnic: avoid double free when failing to DMA-map FW msg

## Summary
Severity: High
Advisory: CVE-2025-38341
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-07-10
Source: https://osv.dev/vulnerability/CVE-2025-38341
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.11.0 <6.12.35, >=6.13.0 <6.15.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

eth: fbnic: avoid double free when failing to DMA-map FW msg

The semantics are that caller of fbnic_mbx_map_msg() retains
the ownership of the message on error. All existing callers
dutifully free the page.

## References
- https://git.kernel.org/stable/c/0a211e23852019ef55c70094524e87a944accbb5
- https://git.kernel.org/stable/c/5bd1bafd4474ee26f504b41aba11f3e2a1175b88
- https://git.kernel.org/stable/c/670179265ad787b9dd8e701601914618b8927755
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38341.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38341
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
