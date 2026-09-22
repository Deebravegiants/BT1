# [H] ALPINE-CVE-2026-71226

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-71226
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:H)
Published: 2026-08-05
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-71226
Type: osv

## Affected
- Alpine:v3.21: `libkcapi` — affected >=0.12.0 <1.5.1-r0
- Alpine:v3.22: `libkcapi` — affected >=0.12.0 <1.5.1-r0
- Alpine:v3.23: `libkcapi` — affected >=0.12.0 <1.5.1-r0
- Alpine:v3.24: `libkcapi` — affected >=0.12.0 <1.5.1-r0

## Details
Memory Corruption via Uncanceled AIO Requests on Error: libkcapi's one-shot AIO path can return an error before all submitted IOCBs are drained, allowing later kernel writes into caller-owned output buffers.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-71226
