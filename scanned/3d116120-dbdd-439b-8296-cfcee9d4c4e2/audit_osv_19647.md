# [H] CVE-2021-23206

## Summary
Severity: High
Advisory: CVE-2021-23206
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-03-02
Source: https://osv.dev/vulnerability/CVE-2021-23206
Type: osv

## Details
A flaw was found in htmldoc in v1.9.12 and prior. A stack buffer overflow in parse_table() in ps-pdf.cxx may lead to execute arbitrary code and denial of service.

## References
- https://ubuntu.com/security/CVE-2021-23206
- https://github.com/michaelrsweet/htmldoc/issues/416
- https://bugzilla.redhat.com/show_bug.cgi?id=1967028
- https://github.com/michaelrsweet/htmldoc/commit/ba61a3ece382389ae4482c7027af8b32e8ab4cc8
