# [M] CVE-2018-20349

## Summary
Severity: Medium
Advisory: CVE-2018-20349
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-12-22
Source: https://osv.dev/vulnerability/CVE-2018-20349
Type: osv

## Details
The igraph_i_strdiff function in igraph_trie.c in igraph through 0.7.1 has an NULL pointer dereference that allows attackers to cause a denial of service (application crash) via a crafted object.

## References
- https://lists.debian.org/debian-lts-announce/2019/12/msg00038.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/NCGDUNQYLSZLSGN6JJBORVFW46U3A75Y/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/OWCGXEINKJM3JQUPVCSN4RBTRKWBTYI7/
- https://github.com/igraph/igraph/issues/1141
