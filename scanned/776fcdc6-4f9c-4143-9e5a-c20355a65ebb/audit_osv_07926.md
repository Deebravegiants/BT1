# [M] broken TLS options for threaded LDAPS

## Summary
Severity: Medium
Advisory: CURL-CVE-2025-14017
Aliases: CVE-2025-14017
Published: 2026-01-07
Source: https://osv.dev/vulnerability/CURL-CVE-2025-14017
Type: osv

## Details
When doing multi-threaded LDAPS transfers (LDAP over TLS) with libcurl,
changing TLS options in one thread would inadvertently change them globally
and therefore possibly also affect other concurrently setup transfers.

Disabling certificate verification for a specific transfer could
unintentionally disable the feature for other threads as well.
