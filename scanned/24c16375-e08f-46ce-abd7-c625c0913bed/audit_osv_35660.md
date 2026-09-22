# [H] CVE-2026-12245

## Summary
Severity: High
Advisory: CVE-2026-12245
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-12245
Type: osv

## Details
NSD from version 4.13.0 has a heap use-after-free bug in logging errors on TLS connections, causing a crash of the server process, which can be triggered trivially by sending a DNS query over a DoT connection, and closing the connection without reading the response.

## References
- https://www.nlnetlabs.nl/downloads/nsd/CVE-2026-12245.txt
