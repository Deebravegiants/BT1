# [M] OCSP stapling bypass with Apple SecTrust

## Summary
Severity: Medium
Advisory: CURL-CVE-2026-7009
Aliases: CVE-2026-7009
Published: 2026-04-29
Source: https://osv.dev/vulnerability/CURL-CVE-2026-7009
Type: osv

## Details
When curl is told to use the Certificate Status Request TLS extension, often
referred to as *OCSP stapling*, to verify that the server certificate is
valid, it fails to detect OCSP problems and instead wrongly consider the
response as fine.
