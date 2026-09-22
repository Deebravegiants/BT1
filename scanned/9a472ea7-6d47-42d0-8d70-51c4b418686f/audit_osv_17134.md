# [M] CVE-2020-12802

## Summary
Severity: Medium
Advisory: CVE-2020-12802
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2020-06-08
Source: https://osv.dev/vulnerability/CVE-2020-12802
Type: osv

## Details
LibreOffice has a 'stealth mode' in which only documents from locations deemed 'trusted' are allowed to retrieve remote resources. This mode is not the default mode, but can be enabled by users who want to disable LibreOffice's ability to include remote resources within a document. A flaw existed where remote graphic links loaded from docx documents were omitted from this protection prior to version 6.4.4. This issue affects: The Document Foundation LibreOffice versions prior to 6.4.4.

## References
- https://lists.debian.org/debian-lts-announce/2023/12/msg00026.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PQIBAKXD7VO5IGBD7ZMH3GGBNR5R2IOA/
- http://lists.opensuse.org/opensuse-security-announce/2020-08/msg00042.html
- http://lists.opensuse.org/opensuse-security-announce/2020-08/msg00058.html
- https://www.libreoffice.org/about-us/security/advisories/CVE-2020-12802
