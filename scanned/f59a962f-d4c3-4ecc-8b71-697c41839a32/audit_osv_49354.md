# [H] CVE-2019-11023

## Summary
Severity: High
Advisory: CVE-2019-11023
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-04-08
Source: https://osv.dev/vulnerability/CVE-2019-11023
Type: osv

## Details
The agroot() function in cgraph\obj.c in libcgraph.a in Graphviz 2.39.20160612.1140 has a NULL pointer dereference, as demonstrated by graphml2gv.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/CLEAHLDJVMAEGA3YMC7KPKJ7ZPXNMJID/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/FI3D5TQE3IMCSF5OUTXQL4GVKFCIY5JG/
- http://lists.opensuse.org/opensuse-security-announce/2019-05/msg00054.html
- http://lists.opensuse.org/opensuse-security-announce/2019-05/msg00065.html
- http://lists.opensuse.org/opensuse-security-announce/2020-06/msg00056.html
- http://lists.opensuse.org/opensuse-security-announce/2020-06/msg00065.html
- https://gitlab.com/graphviz/graphviz/issues/1517
- https://research.loginsoft.com/bugs/null-pointer-dereference-in-function-agroot/
