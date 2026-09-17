# [H] ALPINE-CVE-2026-1144

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-1144
Ecosystem: Alpine:v3.23, Alpine:v3.24
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-01-19
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-1144
Type: osv

## Affected
- Alpine:v3.23: `quickjs-ng` — affected >=0 <0.11.0-r1
- Alpine:v3.24: `quickjs-ng` — affected >=0 <0.11.0-r2

## Details
A vulnerability was detected in quickjs-ng quickjs up to 0.11.0. Affected is an unknown function of the file quickjs.c of the component Atomics Ops Handler. The manipulation results in use after free. The attack can be executed remotely. The exploit is now public and may be used. The patch is identified as ea3e9d77454e8fc9cb3ef3c504e9c16af5a80141. Applying a patch is advised to resolve this issue.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-1144
