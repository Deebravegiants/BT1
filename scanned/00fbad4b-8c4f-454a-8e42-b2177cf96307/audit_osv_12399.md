# [H] CVE-2018-11697

## Summary
Severity: High
Advisory: CVE-2018-11697
CVSS: 8.1 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:H)
Published: 2018-06-04
Source: https://osv.dev/vulnerability/CVE-2018-11697
Type: osv

## Details
An issue was discovered in LibSass through 3.5.4. An out-of-bounds read of a memory region was found in the function Sass::Prelexer::exactly() which could be leveraged by an attacker to disclose information or manipulated to read from unmapped memory causing a denial of service.

## References
- https://github.com/sass/libsass/issues/2656
