# [H] KVM: arm64: nv: Drop bogus WARN for write to ZCR_EL2

## Summary
Severity: High
Advisory: CVE-2026-72280
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:N/I:N/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72280
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.11.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

KVM: arm64: nv: Drop bogus WARN for write to ZCR_EL2

It is entirely possible for a guest to write to the ZCR_EL2 sysreg alias
while in a nested context, as it is expected if FEAT_NV2 is advertised
to the L1 hypervisor.

Get rid of the bogus WARN which, since the hyp vectors were installed at
this point, has the effect of a hyp_panic...

## References
- https://git.kernel.org/stable/c/5000bcae71c869cba6674c326fec2d8ad659ae3a
- https://git.kernel.org/stable/c/6561597dba97e3e8479a9919bda172cf43eb902c
- https://git.kernel.org/stable/c/7deadbc5dab5b8e2316364603bc6281129c8461c
- https://git.kernel.org/stable/c/9f1667098c6ae7ec81a9a56859cfdacb822aa0d0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72280.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72280
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
