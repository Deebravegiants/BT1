# [M] CVE-2022-3140

## Summary
Severity: Medium
Advisory: CVE-2022-3140
CVSS: 6.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:L)
Published: 2022-10-11
Source: https://osv.dev/vulnerability/CVE-2022-3140
Type: osv

## Details
LibreOffice supports Office URI Schemes to enable browser integration of LibreOffice with MS SharePoint server. An additional scheme 'vnd.libreoffice.command' specific to LibreOffice was added. In the affected versions of LibreOffice links using that scheme could be constructed to call internal macros with arbitrary arguments. Which when clicked on, or activated by document events, could result in arbitrary script execution without warning. This issue affects: The Document Foundation LibreOffice 7.4 versions prior to 7.4.1; 7.3 versions prior to 7.3.6.

## References
- https://lists.debian.org/debian-lts-announce/2023/03/msg00022.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/TORANVTIWWBH3DNJR4UZATAG67KZOH32/
- https://security.gentoo.org/glsa/202212-04
- https://www.debian.org/security/2022/dsa-5252
- https://www.libreoffice.org/about-us/security/advisories/CVE-2022-3140
