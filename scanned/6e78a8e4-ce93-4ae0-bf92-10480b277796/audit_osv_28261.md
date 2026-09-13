# [M] CVE-2024-3044

## Summary
Severity: Medium
Advisory: CVE-2024-3044
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:L)
Published: 2024-05-14
Source: https://osv.dev/vulnerability/CVE-2024-3044
Type: osv

## Details
Unchecked script execution in Graphic on-click binding in affected LibreOffice versions allows an attacker to create a document which without prompt will execute scripts built-into LibreOffice on clicking a graphic. Such scripts were previously deemed trusted but are now deemed untrusted.

## References
- https://lists.debian.org/debian-lts-announce/2024/05/msg00016.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/3TU3TYDXICKPYHMCNL7ARYYBXACEAYJ4/
- https://www.libreoffice.org/about-us/security/advisories/CVE-2024-3044
