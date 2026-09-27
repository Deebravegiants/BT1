# [M] JLSEC-2026-90

## Summary
Severity: Medium
Advisory: JLSEC-2026-90
Ecosystem: Julia
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:P/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-04-13
Source: https://osv.dev/vulnerability/JLSEC-2026-90
Type: osv

## Affected
- Julia: `Poppler_jll` — affected >=0 <25.10.0+0

## Details
Poppler is a PDF rendering library. Versions prior to 25.06.0 use `std::atomic_int` for reference counting. Because `std::atomic_int` is only 32 bits, it is possible to overflow the reference count and trigger a use-after-free. Version 25.06.0 patches the issue.

## References
- http://www.openwall.com/lists/oss-security/2025/07/11/5
- http://www.openwall.com/lists/oss-security/2025/07/12/1
- https://gitlab.freedesktop.org/poppler/poppler/-/commit/04bd91684ed41d67ae0f10cde0660e4ed74ac203
- https://gitlab.freedesktop.org/poppler/poppler/-/commit/ac36affcc8486de38e8905a8d6547a3464ff46e5
- https://gitlab.freedesktop.org/poppler/poppler/-/issues/1581
- https://gitlab.freedesktop.org/poppler/poppler/-/merge_requests/1828
- https://securitylab.github.com/advisories/GHSL-2025-054_poppler/
