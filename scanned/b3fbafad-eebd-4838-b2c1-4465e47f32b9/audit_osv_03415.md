# [H] ALPINE-CVE-2026-11352

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-11352
Ecosystem: Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-03
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-11352
Type: osv

## Affected
- Alpine:v3.23: `curl` — affected >=8.18.0 <8.22.0-r0
- Alpine:v3.24: `curl` — affected >=8.18.0 <8.21.0-r0

## Details
An issue in curl’s QUIC UDP receive function allows a malicious HTTP/3 server
to trigger a remote denial of service against a curl or libcurl client.
Because the helper function discards zero-length UDP datagrams before counting
them toward the per-call packet budget, a connected QUIC peer can continuously
stream empty datagrams to indefinitely stall the client.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-11352
