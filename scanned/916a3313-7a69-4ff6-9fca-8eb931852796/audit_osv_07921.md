# [M] HTTP headers eat all memory

## Summary
Severity: Medium
Advisory: CURL-CVE-2023-38039
Aliases: CVE-2023-38039
Published: 2023-09-13
Source: https://osv.dev/vulnerability/CURL-CVE-2023-38039
Type: osv

## Details
When curl retrieves an HTTP response, it stores the incoming headers so that
they can be accessed later via the libcurl headers API.

However, curl did not have a limit on the size or quantity of headers it would
accept in a response, allowing a malicious server to stream an endless series
of headers to a client and eventually cause curl to run out of heap memory.
