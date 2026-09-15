# [H] CVE-2020-35635

## Summary
Severity: High
Advisory: CVE-2020-35635
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-08-30
Source: https://osv.dev/vulnerability/CVE-2020-35635
Type: osv

## Details
A code execution vulnerability exists in the Nef polygon-parsing functionality of CGAL libcgal CGAL-5.1.1 in Nef_S2/SNC_io_parser.h SNC_io_parser::read_sface() store_sm_boundary_item() Sloop_of OOB read. A specially crafted malformed file can lead to an out-of-bounds read and type confusion, which could lead to code execution. An attacker can provide malicious input to trigger this vulnerability.

## References
- https://lists.debian.org/debian-lts-announce/2022/12/msg00011.html
- https://security.gentoo.org/glsa/202305-34
- https://talosintelligence.com/vulnerability_reports/TALOS-2020-1225
