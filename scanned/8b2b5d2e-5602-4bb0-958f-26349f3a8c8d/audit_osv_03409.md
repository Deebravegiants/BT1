# [M] ALPINE-CVE-2026-0864

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-0864
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-06-23
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-0864
Type: osv

## Affected
- Alpine:v3.21: `python3` — affected >=0 <3.12.14-r0
- Alpine:v3.22: `python3` — affected >=0 <3.12.14-r0
- Alpine:v3.23: `python3` — affected >=0 <3.12.14-r0
- Alpine:v3.24: `python3` — affected >=0 <3.14.7-r0

## Details
When using the "configparser" module to write configuration files
containing multi-line text values with carriage return characters (\r) the
resulting file could be injected with unexpected keys and values if the
attacker controls the written value.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-0864
