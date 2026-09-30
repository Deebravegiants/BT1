# [M] Stack overflow in libxml2

## Summary
Severity: Medium
Advisory: CVE-2025-9714
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-10
Source: https://osv.dev/vulnerability/CVE-2025-9714
Type: osv

## Details
Uncontrolled recursion in XPath evaluation in libxml2 up to and including version 2.9.14 allows a local attacker to cause a stack overflow via crafted expressions. XPath processing functions `xmlXPathRunEval`, `xmlXPathCtxtCompile`, and `xmlXPathEvalExpr` were resetting recursion depth to zero before making potentially recursive calls. When such functions were called recursively this could allow for uncontrolled recursion and lead to a stack overflow. These functions now preserve recursion depth across recursive calls, allowing recursion depth to be controlled.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-577017.html
- https://lists.debian.org/debian-lts-announce/2025/09/msg00035.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/9xxx/CVE-2025-9714.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-9714
- https://gitlab.gnome.org/GNOME/libxml2/-/commit/677a42645ef22b5a50741bad5facf9d8a8bc6d21
- https://gitlab.gnome.org/GNOME/libxml2
