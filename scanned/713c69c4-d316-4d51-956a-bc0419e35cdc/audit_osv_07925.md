# [M] No QUIC certificate pinning with GnuTLS

## Summary
Severity: Medium
Advisory: CURL-CVE-2025-13034
Aliases: CVE-2025-13034
Published: 2026-01-07
Source: https://osv.dev/vulnerability/CURL-CVE-2025-13034
Type: osv

## Details
When using `CURLOPT_PINNEDPUBLICKEY` option with libcurl or `--pinnedpubkey`
with the curl tool, curl should check the public key of the server certificate
to verify the peer.

This check was skipped in a certain condition that would then make curl allow
the connection without performing the proper check, thus not noticing a
possible impostor. To skip this check, the connection had to be done with QUIC
with ngtcp2 built to use GnuTLS and the user had to explicitly disable the
standard certificate verification.
