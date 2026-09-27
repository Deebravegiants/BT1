# [C] ALPINE-CVE-2026-0821

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2026-0821
Ecosystem: Alpine:v3.23, Alpine:v3.24
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-01-10
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-0821
Type: osv

## Affected
- Alpine:v3.23: `quickjs-ng` — affected >=0 <0.11.0-r1
- Alpine:v3.24: `quickjs-ng` — affected >=0 <0.11.0-r2

## Details
A vulnerability was determined in quickjs-ng quickjs up to 0.11.0. This vulnerability affects the function js_typed_array_constructor of the file quickjs.c. Executing a manipulation can lead to heap-based buffer overflow. The attack may be launched remotely. The exploit has been publicly disclosed and may be utilized. This patch is called c5d80831e51e48a83eab16ea867be87f091783c5. A patch should be applied to remediate this issue.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-0821
