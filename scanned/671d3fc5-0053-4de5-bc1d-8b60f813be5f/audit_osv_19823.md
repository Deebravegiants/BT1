# [H] CVE-2021-26252

## Summary
Severity: High
Advisory: CVE-2021-26252
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-02-24
Source: https://osv.dev/vulnerability/CVE-2021-26252
Type: osv

## Details
A flaw was found in htmldoc in v1.9.12. Heap buffer overflow in pspdf_prepare_page(),in ps-pdf.cxx may lead to execute arbitrary code and denial of service.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1967009
