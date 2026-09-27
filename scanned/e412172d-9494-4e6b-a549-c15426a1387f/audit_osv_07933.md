# [M] netrc credential leak with reused proxy connection

## Summary
Severity: Medium
Advisory: CURL-CVE-2026-6429
Aliases: CVE-2026-6429
Published: 2026-04-29
Source: https://osv.dev/vulnerability/CURL-CVE-2026-6429
Type: osv

## Details
When asked to both use a `.netrc` file for credentials and to follow HTTP
redirects, libcurl could leak the password used for the first host to the
followed-to host under certain circumstances.
