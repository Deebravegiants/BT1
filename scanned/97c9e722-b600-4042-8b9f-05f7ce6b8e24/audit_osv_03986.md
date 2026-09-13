# [H] ALPINE-CVE-2026-9545

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-9545
Ecosystem: Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-07-03
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-9545
Type: osv

## Affected
- Alpine:v3.23: `curl` — affected >=8.11.0 <8.22.0-r0
- Alpine:v3.24: `curl` — affected >=8.11.0 <8.21.0-r0

## Details
In this scenario, libcurl first uses a proper HTTP/3 server for the initial
transfers, and when it makes a second transfer to the same site it has been
replaced by the attacker's impostor machine - without a valid certificate.

When libcurl returns to the hostname the second time with a cached SSL session
(`CURLOPT_SSL_SESSIONID_CACHE` is not disabled) and early data enabled (the
`CURLSSLOPT_EARLYDATA` bit is set in `CURLOPT_SSL_OPTIONS`), libcurl might
send off the second request's bytes on that new connection *before* enforcing
the certificate verification failure. Potentially leaking sensitive
information.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-9545
