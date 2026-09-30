# [M] CVE-2021-44960

## Summary
Severity: Medium
Advisory: CVE-2021-44960
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-02-15
Source: https://osv.dev/vulnerability/CVE-2021-44960
Type: osv

## Details
In SVGPP SVG++ library 1.3.0, the XMLDocument::getRoot function in the renderDocument function handled the XMLDocument object improperly, returning a null pointer in advance at the second if, resulting in a null pointer reference behind the renderDocument function.

## References
- https://lists.debian.org/debian-lts-announce/2023/04/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/10/msg00016.html
- https://github.com/svgpp/svgpp/issues/101
- https://github.com/svgpp/svgpp/issues/101.aa
