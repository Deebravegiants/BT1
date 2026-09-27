# [H] CVE-2021-26259

## Summary
Severity: High
Advisory: CVE-2021-26259
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-03-03
Source: https://osv.dev/vulnerability/CVE-2021-26259
Type: osv

## Details
A flaw was found in htmldoc in v1.9.12. Heap buffer overflow in render_table_row(),in ps-pdf.cxx may lead to arbitrary code execution and denial of service.

## References
- https://github.com/michaelrsweet/htmldoc/commit/0ddab26a542c74770317b622e985c52430092ba5
- https://github.com/michaelrsweet/htmldoc/issues/417
