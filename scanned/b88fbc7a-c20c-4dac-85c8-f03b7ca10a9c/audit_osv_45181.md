# [H] A flaw was found in how GLib’s GString manages memory when adding data to strings

## Summary
Severity: High
Advisory: JLSEC-2025-167
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-10-19
Source: https://osv.dev/vulnerability/JLSEC-2025-167
Type: osv

## Affected
- Julia: `Glib_jll` — affected >=2.76.5+0 <2.86.0+0

## Details
A flaw was found in how GLib’s GString manages memory when adding data to strings. If a string is already very large, combining it with more input can cause a hidden overflow in the size calculation. This makes the system think it has enough memory when it doesn’t. As a result, data may be written past the end of the allocated memory, leading to crashes or memory corruption.

## References
- https://access.redhat.com/security/cve/CVE-2025-6052
- https://bugzilla.redhat.com/show_bug.cgi?id=2372666
- https://cert-portal.siemens.com/productcert/html/ssa-032379.html
- https://cert-portal.siemens.com/productcert/html/ssa-253495.html
