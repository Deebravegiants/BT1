# [H] CVE-2025-1080

## Summary
Severity: High
Advisory: CVE-2025-1080
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2025-03-04
Source: https://osv.dev/vulnerability/CVE-2025-1080
Type: osv

## Details
LibreOffice supports Office URI Schemes to enable browser integration of LibreOffice with MS SharePoint server. An additional scheme 'vnd.libreoffice.command' specific to LibreOffice was added. In the affected versions of LibreOffice a link in a browser using that scheme could be constructed with an embedded inner URL that when passed to LibreOffice could call internal macros with arbitrary arguments.
This issue affects LibreOffice: from 24.8 before < 24.8.5, from 25.2 before < 25.2.1.

## References
- https://lists.debian.org/debian-lts-announce/2025/06/msg00002.html
- https://www.libreoffice.org/about-us/security/advisories/cve-2025-1080
