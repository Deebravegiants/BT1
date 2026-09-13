# [C] CVE-2020-35628

## Summary
Severity: Critical
Advisory: CVE-2020-35628
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-03-04
Source: https://osv.dev/vulnerability/CVE-2020-35628
Type: osv

## Details
A code execution vulnerability exists in the Nef polygon-parsing functionality of CGAL libcgal CGAL-5.1.1. An oob read vulnerability exists in Nef_S2/SNC_io_parser.h SNC_io_parser::read_sloop() slh->incident_sface. An attacker can provide malicious input to trigger this vulnerability.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/E4J344OKKDLPRN422OYRR46HDEN6MM6P/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/NB5SF5OJR2DSV7CC6U7FVW5VJSJO5EKV/
- https://lists.debian.org/debian-lts-announce/2021/05/msg00002.html
- https://lists.debian.org/debian-lts-announce/2022/12/msg00011.html
- https://security.gentoo.org/glsa/202305-34
- https://talosintelligence.com/vulnerability_reports/TALOS-2020-1225
