# [H] CVE-2021-42533

## Summary
Severity: High
Advisory: CVE-2021-42533
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-03-16
Source: https://osv.dev/vulnerability/CVE-2021-42533
Type: osv

## Details
Adobe Bridge version 11.1.1 (and earlier) is affected by a double free vulnerability when parsing a crafted DCM file, which could result in arbitrary code execution in the context of the current user. This vulnerability requires user interaction to exploit.

## References
- https://helpx.adobe.com/security/products/bridge/apsb21-94.html
