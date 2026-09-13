# [H] SOCKS5 heap buffer overflow

## Summary
Severity: High
Advisory: CURL-CVE-2023-38545
Aliases: CVE-2023-38545
Published: 2023-10-11
Source: https://osv.dev/vulnerability/CURL-CVE-2023-38545
Type: osv

## Details
This flaw makes curl overflow a heap based buffer in the SOCKS5 proxy
handshake.

When curl is asked to pass along the hostname to the SOCKS5 proxy to allow
that to resolve the address instead of it getting done by curl itself, the
maximum length that hostname can be is 255 bytes.

If the hostname is detected to be longer than 255 bytes, curl switches to
local name resolving and instead passes on the resolved address only to the
proxy. Due to a bug, the local variable that means "let the host resolve the
name" could get the wrong value during a slow SOCKS5 handshake, and contrary
to the intention, copy the too long hostname to the target buffer instead of
copying only the resolved address there.
