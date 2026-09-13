# [C] CVE-2021-23165

## Summary
Severity: Critical
Advisory: CVE-2021-23165
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-03-16
Source: https://osv.dev/vulnerability/CVE-2021-23165
Type: osv

## Details
A flaw was found in htmldoc before v1.9.12. Heap buffer overflow in pspdf_prepare_outpages(), in ps-pdf.cxx may lead to execute arbitrary code and denial of service.

## References
- https://github.com/michaelrsweet/htmldoc/commit/6e8a95561988500b5b5ae4861b3b0cbf4fba517f.patch
- https://github.com/michaelrsweet/htmldoc/issues/413
- https://bugzilla.redhat.com/show_bug.cgi?id=1967014
- https://github.com/michaelrsweet/htmldoc/commit/6e8a95561988500b5b5ae4861b3b0cbf4fba517f
