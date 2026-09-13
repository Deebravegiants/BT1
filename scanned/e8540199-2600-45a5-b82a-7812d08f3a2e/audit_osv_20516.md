# [C] CVE-2021-34436

## Summary
Severity: Critical
Advisory: CVE-2021-34436
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-09-02
Source: https://osv.dev/vulnerability/CVE-2021-34436
Type: osv

## Details
In Eclipse Theia 0.1.1 to 0.2.0, it is possible to exploit the default build to obtain remote code execution (and XXE) via the theia-xml-extension. This extension uses lsp4xml (recently renamed to LemMinX) in order to provide language support for XML. This is installed by default.

## References
- https://bugs.eclipse.org/bugs/show_bug.cgi?id=563174
