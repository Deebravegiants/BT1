# [H] ALPINE-CVE-2025-66418

## Summary
Severity: High
Advisory: ALPINE-CVE-2025-66418
Ecosystem: Alpine:v3.23
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-12-05
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-66418
Type: osv

## Affected
- Alpine:v3.23: `py3-urllib3` — affected >=0 <2.6.3-r0

## Details
urllib3 is a user-friendly HTTP client library for Python. Starting in version 1.24 and prior to 2.6.0, the number of links in the decompression chain was unbounded allowing a malicious server to insert a virtually unlimited number of compression steps leading to high CPU usage and massive memory allocation for the decompressed data. This vulnerability is fixed in 2.6.0.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-66418
