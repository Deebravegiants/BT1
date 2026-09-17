# [M] CVE-2024-12426

## Summary
Severity: Medium
Advisory: CVE-2024-12426
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2025-01-07
Source: https://osv.dev/vulnerability/CVE-2024-12426
Type: osv

## Details
Exposure of Environmental Variables and arbitrary INI file values to an Unauthorized Actor vulnerability in The Document Foundation LibreOffice.




URLs could be constructed which expanded environmental variables or INI file values, so potentially sensitive information could be exfiltrated to a remote server on opening a document containing such links.


This issue affects LibreOffice: from 24.8 before < 24.8.4.

## References
- https://lists.debian.org/debian-lts-announce/2025/01/msg00013.html
- https://www.libreoffice.org/about-us/security/advisories/cve-2024-12426
