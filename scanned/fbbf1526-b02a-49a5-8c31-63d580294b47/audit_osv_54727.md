# [H] CVE-2024-31142

## Summary
Severity: High
Advisory: CVE-2024-31142
CVSS: 7.5 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-16
Source: https://osv.dev/vulnerability/CVE-2024-31142
Type: osv

## Details
Because of a logical error in XSA-407 (Branch Type Confusion), the
mitigation is not applied properly when it is intended to be used.
XSA-434 (Speculative Return Stack Overflow) uses the same
infrastructure, so is equally impacted.

For more details, see:
  https://xenbits.xen.org/xsa/advisory-407.html
  https://xenbits.xen.org/xsa/advisory-434.html

## References
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/D5OK6MH75S7YWD34EWW7QIZTS627RIE3/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/RYAZ7P6YFJ2E3FHKAGIKHWS46KYMMTZH/
- https://xenbits.xenproject.org/xsa/advisory-455.html
- http://xenbits.xen.org/xsa/advisory-455.html
