# [H] pmdomain: imx93-blk-ctrl: Extract PHY as shared domain for DSI/CSI

## Summary
Severity: High
Advisory: CVE-2026-72009
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72009
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.1.0 <6.18.42, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

pmdomain: imx93-blk-ctrl: Extract PHY as shared domain for DSI/CSI

The MIPI DSI and CSI domains share control bits for clock and reset, which
can lead to incorrect behavior if one domain disables the shared resource
while the other is still active.

To fix the issue, introduce a shared MIPI PHY power domain to own the
common resources and make DSI and CSI its subdomains. This ensures the
shared bits are properly managed and not disabled while still in use.

## References
- https://git.kernel.org/stable/c/4ba6d7166750d0b810c6cfc0b1df7585f513b48c
- https://git.kernel.org/stable/c/4fd5b33faf092ef2d09f730a7d9e49f9e976ac67
- https://git.kernel.org/stable/c/99611233f8cda833169fa6487d5dacdf189e5cb0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72009.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72009
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
