# [M] CVE-2018-1000069

## Summary
Severity: Medium
Advisory: CVE-2018-1000069
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2018-03-13
Source: https://osv.dev/vulnerability/CVE-2018-1000069
Type: osv

## Details
FreePlane version 1.5.9 and earlier contains a XML External Entity (XXE) vulnerability in XML Parser in mindmap loader that can result in stealing data from victim's machine. This attack appears to require the victim to open a specially crafted mind map file. This vulnerability appears to have been fixed in 1.6+.

## References
- https://lists.debian.org/debian-lts-announce/2018/03/msg00019.html
- https://www.debian.org/security/2018/dsa-4175
- https://www.freeplane.org/wiki/index.php/XML_External_Entity_vulnerability_in_map_parser
- https://www.youtube.com/watch?v=7IXtiTNilAI
