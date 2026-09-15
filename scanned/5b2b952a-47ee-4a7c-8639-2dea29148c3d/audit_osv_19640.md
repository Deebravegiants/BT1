# [C] CVE-2021-23158

## Summary
Severity: Critical
Advisory: CVE-2021-23158
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-03-16
Source: https://osv.dev/vulnerability/CVE-2021-23158
Type: osv

## Details
A flaw was found in htmldoc in v1.9.12. Double-free in function pspdf_export(),in ps-pdf.cxx may result in a write-what-where condition, allowing an attacker to execute arbitrary code and denial of service.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1967018
- https://github.com/michaelrsweet/htmldoc/issues/414
- https://github.com/michaelrsweet/htmldoc/commit/369b2ea1fd0d0537ba707f20a2f047b6afd2fbdc
