# [C] CVE-2020-35636

## Summary
Severity: Critical
Advisory: CVE-2020-35636
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-03-04
Source: https://osv.dev/vulnerability/CVE-2020-35636
Type: osv

## Details
A code execution vulnerability exists in the Nef polygon-parsing functionality of CGAL libcgal CGAL-5.1.1 in Nef_S2/SNC_io_parser.h SNC_io_parser::read_sface() sfh->volume() OOB read. A specially crafted malformed file can lead to an out-of-bounds read and type confusion, which could lead to code execution. An attacker can provide malicious input to trigger this vulnerability.

## References
- https://lists.debian.org/debian-lts-announce/2022/12/msg00011.html
- https://security.gentoo.org/glsa/202305-34
- https://talosintelligence.com/vulnerability_reports/TALOS-2020-1225
