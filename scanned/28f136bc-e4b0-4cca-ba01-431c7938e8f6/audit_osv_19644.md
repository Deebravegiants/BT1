# [H] CVE-2021-23180

## Summary
Severity: High
Advisory: CVE-2021-23180
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-03-02
Source: https://osv.dev/vulnerability/CVE-2021-23180
Type: osv

## Details
A flaw was found in htmldoc in v1.9.12 and before. Null pointer dereference in file_extension(),in file.c may lead to execute arbitrary code and denial of service.

## References
- https://ubuntu.com/security/CVE-2021-23180
- https://github.com/michaelrsweet/htmldoc/issues/418
- https://bugzilla.redhat.com/show_bug.cgi?id=1967041
- https://github.com/michaelrsweet/htmldoc/commit/19c582fb32eac74b57e155cffbb529377a9e751a
