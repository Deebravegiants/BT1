# [H] JLSEC-2026-84

## Summary
Severity: High
Advisory: JLSEC-2026-84
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-13
Source: https://osv.dev/vulnerability/JLSEC-2026-84
Type: osv

## Affected
- Julia: `Poppler_jll` — affected >=0 <24.6.0+0

## Details
A flaw was found in the Poppler's Pdfinfo utility. This issue occurs when using -dests parameter with pdfinfo utility. By using certain malformed input files, an attacker could cause the utility to crash, leading to a denial of service.

## References
- https://access.redhat.com/errata/RHSA-2024:5305
- https://access.redhat.com/errata/RHSA-2024:9167
- https://access.redhat.com/security/cve/CVE-2024-6239
- https://bugzilla.redhat.com/show_bug.cgi?id=2293594
