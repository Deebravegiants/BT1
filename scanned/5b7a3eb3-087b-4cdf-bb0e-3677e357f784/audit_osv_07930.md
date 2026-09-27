# [M] use after free in SMB connection reuse

## Summary
Severity: Medium
Advisory: CURL-CVE-2026-3805
Aliases: CVE-2026-3805
Published: 2026-03-11
Source: https://osv.dev/vulnerability/CURL-CVE-2026-3805
Type: osv

## Details
When doing a second SMB request to the same host again, curl would wrongly use
a data pointer pointing into already freed memory.
