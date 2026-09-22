# [H] ALPINE-CVE-2024-52006

## Summary
Severity: High
Advisory: ALPINE-CVE-2024-52006
Ecosystem: Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-01-14
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-52006
Type: osv

## Affected
- Alpine:v3.18: `git` — affected >=2.41.0 <2.40.4-r0
- Alpine:v3.19: `git` — affected >=2.41.0 <2.43.6-r0
- Alpine:v3.20: `git` — affected >=2.41.0 <2.45.3-r0
- Alpine:v3.21: `git` — affected >=2.41.0 <2.47.2-r0
- Alpine:v3.22: `git` — affected >=2.41.0 <2.48.1-r0
- Alpine:v3.23: `git` — affected >=2.41.0 <2.48.1-r0
- Alpine:v3.24: `git` — affected >=2.41.0 <2.48.1-r0

## Details
Git is a fast, scalable, distributed revision control system with an unusually rich command set that provides both high-level operations and full access to internals. Git defines a line-based protocol that is used to exchange information between Git and Git credential helpers. Some ecosystems (most notably, .NET and node.js) interpret single Carriage Return characters as newlines, which renders the protections against CVE-2020-5260 incomplete for credential helpers that treat Carriage Returns in this way. This issue has been addressed in commit `b01b9b8` which is included in release versions v2.48.1, v2.47.2, v2.46.3, v2.45.3, v2.44.3, v2.43.6, v2.42.4, v2.41.3, and v2.40.4. Users are advised to upgrade. Users unable to upgrade should avoid cloning from untrusted URLs, especially recursive clones.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-52006
