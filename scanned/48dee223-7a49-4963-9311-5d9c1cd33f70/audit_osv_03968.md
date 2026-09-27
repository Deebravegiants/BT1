# [H] ALPINE-CVE-2026-80231

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-80231
Ecosystem: Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-09-06
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-80231
Type: osv

## Affected
- Alpine:v3.23: `curl` — affected >=0 <8.22.0-r0
- Alpine:v3.24: `curl` — affected >=0 <8.22.0-r0

## Details
A flaw in libcurl makes it wrongly reuse an existing HTTPS connection setup
for a given hostname even when using a different Native CA Store setting
(`CURLSSLOPT_NATIVE_CA`) than when the connection was created.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-80231
