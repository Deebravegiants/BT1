# [H] ALPINE-CVE-2026-0822

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-0822
Ecosystem: Alpine:v3.23, Alpine:v3.24
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-01-10
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-0822
Type: osv

## Affected
- Alpine:v3.23: `quickjs-ng` — affected >=0 <0.11.0-r1
- Alpine:v3.24: `quickjs-ng` — affected >=0 <0.11.0-r2

## Details
A vulnerability was identified in quickjs-ng quickjs up to 0.11.0. This issue affects the function js_typed_array_sort of the file quickjs.c. The manipulation leads to heap-based buffer overflow. Remote exploitation of the attack is possible. The exploit is publicly available and might be used. The identifier of the patch is 53eefbcd695165a3bd8c584813b472cb4a69fbf5. To fix this issue, it is recommended to deploy a patch.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-0822
