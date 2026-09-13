# [H] CVE-2021-42860

## Summary
Severity: High
Advisory: CVE-2021-42860
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-05-26
Source: https://osv.dev/vulnerability/CVE-2021-42860
Type: osv

## Details
A stack buffer overflow exists in Mini-XML v3.2. When inputting an unformed XML string to the mxmlLoadString API, it will cause a stack-buffer-overflow in mxml_string_getc:2611. NOTE: it is unclear whether this input is allowed by the API specification

## References
- https://github.com/michaelrsweet/mxml/issues/286
