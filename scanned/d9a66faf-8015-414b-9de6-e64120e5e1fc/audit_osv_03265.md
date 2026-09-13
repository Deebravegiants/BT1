# [C] ALPINE-CVE-2025-3277

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2025-3277
Ecosystem: Alpine:v3.21
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-04-14
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-3277
Type: osv

## Affected
- Alpine:v3.21: `sqlite` — affected >=3.44.0 <3.48.0-r1

## Details
An integer overflow can be triggered in SQLite’s `concat_ws()` function. The resulting, truncated integer is then used to allocate a buffer. When SQLite then writes the resulting string to the buffer, it uses the original, untruncated size and thus a wild Heap Buffer overflow of size ~4GB can be triggered. This can result in arbitrary code execution.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-3277
