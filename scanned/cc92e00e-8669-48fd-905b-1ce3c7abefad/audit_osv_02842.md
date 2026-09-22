# [M] ALPINE-CVE-2023-34328

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2023-34328
Ecosystem: Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-01-05
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-34328
Type: osv

## Affected
- Alpine:v3.15: `xen` — affected >=4.5.0 <4.15.5-r3
- Alpine:v3.16: `xen` — affected >=4.5.0 <4.16.5-r3
- Alpine:v3.17: `xen` — affected >=4.5.0 <4.16.5-r3
- Alpine:v3.18: `xen` — affected >=4.5.0 <4.17.2-r3
- Alpine:v3.19: `xen` — affected >=4.5.0 <4.17.2-r3
- Alpine:v3.20: `xen` — affected >=4.5.0 <4.17.2-r3
- Alpine:v3.21: `xen` — affected >=4.5.0 <4.17.2-r3
- Alpine:v3.22: `xen` — affected >=4.5.0 <4.17.2-r3
- Alpine:v3.23: `xen` — affected >=4.5.0 <4.17.2-r3
- Alpine:v3.24: `xen` — affected >=4.5.0 <4.17.2-r3

## Details
[This CNA information record relates to multiple CVEs; the
text explains which aspects/vulnerabilities correspond to which CVE.]

AMD CPUs since ~2014 have extensions to normal x86 debugging functionality.
Xen supports guests using these extensions.

Unfortunately there are errors in Xen's handling of the guest state, leading
to denials of service.

 1) CVE-2023-34327 - An HVM vCPU can end up operating in the context of
    a previous vCPUs debug mask state.

 2) CVE-2023-34328 - A PV vCPU can place a breakpoint over the live GDT.
    This allows the PV vCPU to exploit XSA-156 / CVE-2015-8104 and lock
    up the CPU entirely.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-34328
