# [C] Stack-based Buffer Overflow vulnerability in libmodbus v3.1.10 allows to overflow the buffer...

## Summary
Severity: Critical
Advisory: JLSEC-2026-1252
Ecosystem: Julia
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/JLSEC-2026-1252
Type: osv

## Affected
- Julia: `LibModbus_jll` — affected >=3.1.10+0 <3.1.12+0

## Details
Stack-based Buffer Overflow vulnerability in libmodbus v3.1.10 allows to overflow the buffer allocated for the Modbus response if the function tries to reply to a Modbus request with an
unexpected length.

## References
- https://github.com/advisories/GHSA-96xh-5wq4-m4cc
- https://lists.debian.org/debian-lts-announce/2025/03/msg00010.html
- https://lists.debian.org/debian-lts-announce/2026/08/msg00003.html
- https://nvd.nist.gov/vuln/detail/CVE-2024-10918
- https://www.nozominetworks.com/labs/vulnerability-advisories-cve-2024-10918
