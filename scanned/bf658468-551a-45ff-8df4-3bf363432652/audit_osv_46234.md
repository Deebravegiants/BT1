# [M] A floating-point exception in the PSStack::roll function of Poppler before 25.04.0 can cause an...

## Summary
Severity: Medium
Advisory: JLSEC-2026-85
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-04-13
Source: https://osv.dev/vulnerability/JLSEC-2026-85
Type: osv

## Affected
- Julia: `Poppler_jll` — affected >=0 <25.10.0+0

## Details
A floating-point exception in the PSStack::roll function of Poppler before 25.04.0 can cause an application to crash when handling malformed inputs associated with `INT_MIN`.

## References
- https://github.com/advisories/GHSA-69gq-2xc5-f33j
- https://gitlab.freedesktop.org/poppler/poppler/-/commit/d87bc726c7cc98f8c26b60ece5f20236e9de1bc3
- https://gitlab.freedesktop.org/poppler/poppler/-/issues/1574
- https://lists.debian.org/debian-lts-announce/2025/04/msg00037.html
- https://nvd.nist.gov/vuln/detail/CVE-2025-32364
