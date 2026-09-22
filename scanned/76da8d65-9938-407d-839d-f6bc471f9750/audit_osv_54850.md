# [C] CVE-2024-5261

## Summary
Severity: Critical
Advisory: CVE-2024-5261
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-06-25
Source: https://osv.dev/vulnerability/CVE-2024-5261
Type: osv

## Details
Improper Certificate Validation vulnerability in LibreOffice "LibreOfficeKit" mode disables TLS certification verification

LibreOfficeKit can be used for accessing LibreOffice functionality 
through C/C++. Typically this is used by third party components to reuse
 LibreOffice as a library to convert, view or otherwise interact with 
documents.

LibreOffice internally makes use of "curl" to fetch remote resources such as images hosted on webservers.

In
 affected versions of LibreOffice, when used in LibreOfficeKit mode 
only, then curl's TLS certification verification was disabled 
(CURLOPT_SSL_VERIFYPEER of false)

In the fixed versions curl operates in LibreOfficeKit mode the same as in standard mode with CURLOPT_SSL_VERIFYPEER of true.

This issue affects LibreOffice before version 24.2.4.

## References
- https://www.libreoffice.org/about-us/security/advisories/cve-2024-5261
