# [H] ALPINE-CVE-2026-12932

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-12932
Ecosystem: Alpine:v3.24
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-12932
Type: osv

## Affected
- Alpine:v3.24: `openvpn` — affected >=2.5.0 <2.7.5-r0

## Details
A memory leak in the tls-crypt-v2 client key extraction in OpenVPN 2.5.0 through 2.6.20 and 2.7_alpha1 through 2.7.4 allows remote attackers to cause a denial of service (memory exhaustion) via a flood of crafted packets

## References
- https://security.alpinelinux.org/vuln/CVE-2026-12932
