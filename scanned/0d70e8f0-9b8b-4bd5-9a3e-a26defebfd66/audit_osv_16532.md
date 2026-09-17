# [C] CVE-2019-7653

## Summary
Severity: Critical
Advisory: CVE-2019-7653
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-02-09
Source: https://osv.dev/vulnerability/CVE-2019-7653
Type: osv

## Details
The Debian python-rdflib-tools 4.2.2-1 package for RDFLib 4.2.2 has CLI tools that can load Python modules from the current working directory, allowing code injection, because "python -m" looks in this directory, as demonstrated by rdf2dot. This issue is specific to use of the debian/scripts directory.

## References
- https://lists.debian.org/debian-lts-announce/2019/03/msg00019.html
- https://lists.debian.org/debian-lts-announce/2021/12/msg00026.html
- https://usn.ubuntu.com/4535-1/
- https://bugs.debian.org/921751
