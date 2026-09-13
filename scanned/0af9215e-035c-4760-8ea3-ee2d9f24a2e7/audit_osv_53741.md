# [M] CVE-2023-2255

## Summary
Severity: Medium
Advisory: CVE-2023-2255
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2023-05-25
Source: https://osv.dev/vulnerability/CVE-2023-2255
Type: osv

## Details
Improper access control in editor components of The Document Foundation LibreOffice allowed an attacker to craft a document that would cause external links to be loaded without prompt. In the affected versions of LibreOffice documents that used "floating frames" linked to external files, would load the contents of those frames without prompting the user for permission to do so. This was inconsistent with the treatment of other linked content in LibreOffice. This issue affects: The Document Foundation LibreOffice 7.4 versions prior to 7.4.7; 7.5 versions prior to 7.5.3.

## References
- https://lists.debian.org/debian-lts-announce/2023/08/msg00014.html
- https://www.libreoffice.org/about-us/security/advisories/CVE-2023-2255
- https://security.gentoo.org/glsa/202311-15
- https://www.debian.org/security/2023/dsa-5415
