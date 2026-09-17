# [H] ALPINE-CVE-2026-47895

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-47895
Ecosystem: Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-22
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-47895
Type: osv

## Affected
- Alpine:v3.24: `strongswan` — affected >=0 <6.0.7-r0

## Details
In strongSwan before 6.0.7, identity parsing/cloning is mishandled. Parsed EAP-Identities that result in an empty but non-NULL encoding are not correctly cloned and trigger a double-free once the duplicates are destroyed.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-47895
