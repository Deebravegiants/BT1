# [C] CVE-2018-11210

## Summary
Severity: Critical
Advisory: CVE-2018-11210
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-05-16
Source: https://osv.dev/vulnerability/CVE-2018-11210
Type: osv

## Details
TinyXML2 6.2.0 has a heap-based buffer over-read in the XMLDocument::Parse function in libtinyxml2.so. NOTE: The tinyxml2 developers have determined that the reported overflow is due to improper use of the library and not a vulnerability in tinyxml2

## References
- https://github.com/leethomason/tinyxml2/issues/675
- https://github.com/leethomason/tinyxml2/issues/675#issuecomment-439933437
- https://github.com/leethomason/tinyxml2/issues/675#issuecomment-462194018
