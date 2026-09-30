# [H] CVE-2020-28633

## Summary
Severity: High
Advisory: CVE-2020-28633
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-04-18
Source: https://osv.dev/vulnerability/CVE-2020-28633
Type: osv

## Details
Multiple code execution vulnerabilities exists in the Nef polygon-parsing functionality of CGAL libcgal CGAL-5.1.1. A specially crafted malformed file can lead to an out-of-bounds read and type confusion, which could lead to code execution. An attacker can provide malicious input to trigger any of these vulnerabilities. An oob read vulnerability exists in Nef_S2/SNC_io_parser.h SNC_io_parser<EW>::read_sedge() seh->prev().

## References
- https://lists.debian.org/debian-lts-announce/2022/12/msg00011.html
- https://security.gentoo.org/glsa/202305-34
- https://talosintelligence.com/vulnerability_reports/TALOS-2020-1225
