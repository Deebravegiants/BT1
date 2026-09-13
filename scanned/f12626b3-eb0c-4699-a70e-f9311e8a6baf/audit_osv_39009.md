# [H] net: ipa: fix event ring index not programmed for IPA v5.0+

## Summary
Severity: High
Advisory: CVE-2026-43345
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-05-08
Source: https://osv.dev/vulnerability/CVE-2026-43345
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.4.0 <6.6.136, >=6.7.0 <6.12.83, >=6.13.0 <6.18.24, >=6.19.0 <6.19.14

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: ipa: fix event ring index not programmed for IPA v5.0+

For IPA v5.0+, the event ring index field moved from CH_C_CNTXT_0 to
CH_C_CNTXT_1. The v5.0 register definition intended to define this
field in the CH_C_CNTXT_1 fmask array but used the old identifier of
ERINDEX instead of CH_ERINDEX.

Without a valid event ring, GSI channels could never signal transfer
completions. This caused gsi_channel_trans_quiesce() to block
forever in wait_for_completion().

At least for IPA v5.2 this resolves an issue seen where runtime
suspend, system suspend, and remoteproc stop all hanged forever. It
also meant the IPA data path was completely non functional.

## References
- https://git.kernel.org/stable/c/2bf18b643c4656413f7cfd5615af60a6b4e261da
- https://git.kernel.org/stable/c/2d2dc166d55148cfcf8ae67b415f8d6d110e6fca
- https://git.kernel.org/stable/c/34c988bb04cbdf093d2134e179433da49ffcd044
- https://git.kernel.org/stable/c/56007972c0b1e783ca714d6f1f4d6e66e531d21f
- https://git.kernel.org/stable/c/ae8343a19ccb051d519dbb3a9082ddea9f0551d3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43345.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43345
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
