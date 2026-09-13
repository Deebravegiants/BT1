# [M] CVE-2019-9904

## Summary
Severity: Medium
Advisory: CVE-2019-9904
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-03-21
Source: https://osv.dev/vulnerability/CVE-2019-9904
Type: osv

## Details
An issue was discovered in lib\cdt\dttree.c in libcdt.a in graphviz 2.40.1. Stack consumption occurs because of recursive agclose calls in lib\cgraph\graph.c in libcgraph.a, related to agfstsubg in lib\cgraph\subg.c.

## References
- https://security.gentoo.org/glsa/202107-04
- https://gitlab.com/graphviz/graphviz/issues/1512
- https://research.loginsoft.com/bugs/stack-buffer-overflow-in-function-agclose-graphviz/
