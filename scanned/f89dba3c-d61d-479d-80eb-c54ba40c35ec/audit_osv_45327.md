# [M] Uncontrolled recursion in XPath evaluation in libxml2 up to and including version 2.9.14 allows a...

## Summary
Severity: Medium
Advisory: JLSEC-2025-91
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-10-17
Source: https://osv.dev/vulnerability/JLSEC-2025-91
Type: osv

## Affected
- Julia: `XML2_jll` — affected >=0 <2.10.3+0

## Details
Uncontrolled recursion in XPath evaluation in libxml2 up to and including version 2.9.14 allows a local attacker to cause a stack overflow via crafted expressions. XPath processing functions `xmlXPathRunEval`, `xmlXPathCtxtCompile`, and `xmlXPathEvalExpr` were resetting recursion depth to zero before making potentially recursive calls. When such functions were called recursively this could allow for uncontrolled recursion and lead to a stack overflow. These functions now preserve recursion depth across recursive calls, allowing recursion depth to be controlled.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-577017.html
- https://gitlab.gnome.org/GNOME/libxml2/-/commit/677a42645ef22b5a50741bad5facf9d8a8bc6d21
- https://lists.debian.org/debian-lts-announce/2025/09/msg00035.html
