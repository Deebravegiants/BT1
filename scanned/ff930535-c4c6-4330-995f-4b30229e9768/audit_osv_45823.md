# [H] JLSEC-2026-372

## Summary
Severity: High
Advisory: JLSEC-2026-372
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-30
Source: https://osv.dev/vulnerability/JLSEC-2026-372
Type: osv

## Affected
- Julia: `Mongoose_jll` — affected >=0 <7.21.0+0

## Details
A weakness has been identified in Cesanta Mongoose up to 7.20. This vulnerability affects the function `handle_opt` of the file `/src/net_builtin.c` of the component TCP Option Handler. This manipulation of the argument optlen causes infinite loop. The attack is possible to be carried out remotely. The exploit has been made available to the public and could be used for attacks. Upgrading to version 7.21 is able to resolve this issue. Upgrading the affected component is advised. VulDB has contacted the vendor early and they confirmed quickly, that this issue got fixed already.

## References
- https://github.com/cesanta/mongoose/releases/tag/7.21
- https://github.com/dwBruijn/CVEs/blob/main/Mongoose/TCP_opt_dos.md
- https://vuldb.com/submit/796230
- https://vuldb.com/vuln/359528
- https://vuldb.com/vuln/359528/cti
