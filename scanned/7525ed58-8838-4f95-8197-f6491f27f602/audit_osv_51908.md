# [M] CVE-2021-44961

## Summary
Severity: Medium
Advisory: CVE-2021-44961
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-03-01
Source: https://osv.dev/vulnerability/CVE-2021-44961
Type: osv

## Details
A memory leakage flaw exists in the class PerimeterGenerator of Slic3r libslic3r 1.3.0 and Master Commit b1a5500. Specially crafted stl files can exhaust available memory. An attacker can provide malicious files to trigger this vulnerability.

## References
- http://libslic3r.com
- http://slic3r.com
- https://hackmd.io/nDT_UKLyRQendxDwil9A4w
