# [H] JLSEC-2026-101

## Summary
Severity: High
Advisory: JLSEC-2026-101
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-14
Source: https://osv.dev/vulnerability/JLSEC-2026-101
Type: osv

## Affected
- Julia: `Deno_jll` — affected >=0 <1.33.4+0

## Details
Versions of the package deno before 1.31.0 are vulnerable to Regular Expression Denial of Service (ReDoS) due to the upgradeWebSocket function, which contains regexes in the form of `/s*,s*/`, used for splitting the Connection/Upgrade header. A specially crafted Connection/Upgrade header can be used to significantly slow down a web socket server.

## References
- https://github.com/denoland/deno/blob/2b247be517d789a37e532849e2e40b724af0918f/ext/http/01_http.js%23L395-L409
- https://github.com/denoland/deno/commit/cf06a7c7e672880e1b38598fe445e2c50b4a9d06
- https://github.com/denoland/deno/pull/17722
- https://github.com/denoland/deno/releases/tag/v1.31.0
- https://security.snyk.io/vuln/SNYK-RUST-DENO-3315970
