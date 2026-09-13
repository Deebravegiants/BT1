# [H] CVE-2026-12490

## Summary
Severity: High
Advisory: CVE-2026-12490
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-12490
Type: osv

## Details
When a provide-xfr is given with a tls-auth-name, a secondary requesting a transfer should provide a client certificate with that name. However, no client certificate is needed when the request comes in over TLS over the regular tls-port (and not the tls-auth-port) or over over TCP over the regular port, when the other conditions of the provide-xfr rule match.

## References
- https://www.nlnetlabs.nl/downloads/nsd/CVE-2026-12490.txt
