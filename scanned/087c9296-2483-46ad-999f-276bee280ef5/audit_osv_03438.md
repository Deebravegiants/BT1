# [H] ALPINE-CVE-2026-13117

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-13117
Ecosystem: Alpine:v3.24
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-13117
Type: osv

## Affected
- Alpine:v3.24: `openvpn` — affected >=2.6.0 <2.7.5-r0

## Details
An incomplete guard in OpenVPN 2.6.0 through 2.6.20 and 2.7_alpha1 through 2.7.4 allows remote authenticated peers to trigger a use-after-free during TLS session promotion, potentially leading to a denial of service or memory leakage

## References
- https://security.alpinelinux.org/vuln/CVE-2026-13117
