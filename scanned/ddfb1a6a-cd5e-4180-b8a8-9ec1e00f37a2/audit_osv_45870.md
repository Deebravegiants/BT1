# [M] When using `CURLOPT_PINNEDPUBLICKEY` option with libcurl or `--pinnedpubkey` with the curl tool,curl...

## Summary
Severity: Medium
Advisory: JLSEC-2026-426
Ecosystem: Julia
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-05-04
Source: https://osv.dev/vulnerability/JLSEC-2026-426
Type: osv

## Affected
- Julia: `CURL_jll` — affected >=8.9.0+0 <8.20.0+0
- Julia: `LibCURL_jll` — affected >=8.8.0+0 <8.18.0+0

## Details
When using `CURLOPT_PINNEDPUBLICKEY` option with libcurl or `--pinnedpubkey`
with the curl tool,curl should check the public key of the server certificate
to verify the peer.

This check was skipped in a certain condition that would then make curl allow
the connection without performing the proper check, thus not noticing a
possible impostor. To skip this check, the connection had to be done with QUIC
with ngtcp2 built to use GnuTLS and the user had to explicitly disable the
standard certificate verification.

## References
- https://curl.se/docs/CVE-2025-13034.html
- https://curl.se/docs/CVE-2025-13034.json
- https://github.com/advisories/GHSA-9r76-qj98-jfhc
- https://nvd.nist.gov/vuln/detail/CVE-2025-13034
