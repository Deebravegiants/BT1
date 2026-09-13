# [M] ALPINE-CVE-2024-50349

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2024-50349
Ecosystem: Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 4.7 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:N/I:L/A:N)
Published: 2025-01-14
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-50349
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
Git is a fast, scalable, distributed revision control system with an unusually rich command set that provides both high-level operations and full access to internals. When Git asks for credentials via a terminal prompt (i.e. without using any credential helper), it prints out the host name for which the user is expected to provide a username and/or a password. At this stage, any URL-encoded parts have been decoded already, and are printed verbatim. This allows attackers to craft URLs that contain ANSI escape sequences that the terminal interpret to confuse users e.g. into providing passwords for trusted Git hosting sites when in fact they are then sent to untrusted sites that are under the attacker's control. This issue has been patch via commits `7725b81` and `c903985` which are included in release versions v2.48.1, v2.47.2, v2.46.3, v2.45.3, v2.44.3, v2.43.6, v2.42.4, v2.41.3, and v2.40.4. Users are advised to upgrade. Users unable to upgrade should avoid cloning from untrusted URLs, especially recursive clones.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-50349
