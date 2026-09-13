# [C] ALPINE-CVE-2023-38545

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2023-38545
Ecosystem: Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-10-18
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-38545
Type: osv

## Affected
- Alpine:v3.15: `curl` — affected >=0 <8.4.0-r0
- Alpine:v3.16: `curl` — affected >=0 <8.4.0-r0
- Alpine:v3.17: `curl` — affected >=0 <8.4.0-r0
- Alpine:v3.18: `curl` — affected >=0 <8.4.0-r0
- Alpine:v3.19: `curl` — affected >=0 <8.4.0-r0
- Alpine:v3.20: `curl` — affected >=0 <8.4.0-r0
- Alpine:v3.21: `curl` — affected >=0 <8.4.0-r0
- Alpine:v3.22: `curl` — affected >=0 <8.4.0-r0
- Alpine:v3.23: `curl` — affected >=0 <8.4.0-r0
- Alpine:v3.24: `curl` — affected >=0 <8.4.0-r0

## Details
This flaw makes curl overflow a heap based buffer in the SOCKS5 proxy
handshake.

When curl is asked to pass along the host name to the SOCKS5 proxy to allow
that to resolve the address instead of it getting done by curl itself, the
maximum length that host name can be is 255 bytes.

If the host name is detected to be longer, curl switches to local name
resolving and instead passes on the resolved address only. Due to this bug,
the local variable that means "let the host resolve the name" could get the
wrong value during a slow SOCKS5 handshake, and contrary to the intention,
copy the too long host name to the target buffer instead of copying just the
resolved address there.

The target buffer being a heap based buffer, and the host name coming from the
URL that curl has been told to operate with.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-38545
