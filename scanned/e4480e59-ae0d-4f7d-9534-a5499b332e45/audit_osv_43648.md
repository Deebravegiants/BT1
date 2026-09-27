# [H] octeontx2-af: Block VFs from clobbering special CGX PKIND state

## Summary
Severity: High
Advisory: CVE-2026-74527
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74527
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.20.0 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

octeontx2-af: Block VFs from clobbering special CGX PKIND state

PF and VF NIX LFs that share a CGX LMAC reuse the same hardware PKIND
programming. When HiGig2 or EDSA parsing is enabled, a VF NIX LF alloc must
not reset the LMAC RX PKIND or default TX parse config over the PF setup.

Add cgx_get_pkind() and rvu_cgx_is_pkind_config_permitted() so VFs skip
cgx_set_pkind(), rvu_npc_set_pkind(), and NIX_AF_LFX_TX_PARSE_CFG updates
when the LMAC is using NPC_RX_HIGIG_PKIND or NPC_RX_EDSA_PKIND.

## References
- https://git.kernel.org/stable/c/3bd438a58e910db5dc369aa25dfed1fc95f1b596
- https://git.kernel.org/stable/c/d3c6b0f48f126a36955b3fb4154a59d0b3621d97
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74527.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74527
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
