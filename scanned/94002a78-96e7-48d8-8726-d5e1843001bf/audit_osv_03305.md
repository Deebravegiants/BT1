# [H] ALPINE-CVE-2025-48384

## Summary
Severity: High
Advisory: ALPINE-CVE-2025-48384
Ecosystem: Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.0 (CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:C/C:H/I:H/A:H)
Published: 2025-07-08
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-48384
Type: osv

## Affected
- Alpine:v3.19: `git` — affected >=2.44.0 <2.43.7-r0
- Alpine:v3.20: `git` — affected >=2.44.0 <2.45.4-r0
- Alpine:v3.21: `git` — affected >=2.44.0 <2.47.3-r0
- Alpine:v3.22: `git` — affected >=2.44.0 <2.49.1-r0
- Alpine:v3.23: `git` — affected >=2.44.0 <2.50.1-r0
- Alpine:v3.24: `git` — affected >=2.44.0 <2.50.1-r0

## Details
Git is a fast, scalable, distributed revision control system with an unusually rich command set that provides both high-level operations and full access to internals. When reading a config value, Git strips any trailing carriage return and line feed (CRLF). When writing a config entry, values with a trailing CR are not quoted, causing the CR to be lost when the config is later read. When initializing a submodule, if the submodule path contains a trailing CR, the altered path is read resulting in the submodule being checked out to an incorrect location. If a symlink exists that points the altered path to the submodule hooks directory, and the submodule contains an executable post-checkout hook, the script may be unintentionally executed after checkout. This vulnerability is fixed in v2.43.7, v2.44.4, v2.45.4, v2.46.4, v2.47.3, v2.48.2, v2.49.1, and v2.50.1.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-48384
