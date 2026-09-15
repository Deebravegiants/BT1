# [M] JLSEC-2026-88

## Summary
Severity: Medium
Advisory: JLSEC-2026-88
Ecosystem: Julia
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-04-13
Source: https://osv.dev/vulnerability/JLSEC-2026-88
Type: osv

## Affected
- Julia: `Poppler_jll` — affected >=0 <25.10.0+0

## Details
An issue in the pdfseparate utility of freedesktop poppler v25.04.0 allows attackers to cause an infinite recursion via supplying a crafted PDF file. This can lead to a Denial of Service (DoS).

## References
- http://freedesktop.com
- http://poppler.com
- https://github.com/Landw-hub/CVE-2025-50420
