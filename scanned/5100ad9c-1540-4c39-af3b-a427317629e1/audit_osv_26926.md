# [H] CVE-2023-6186

## Summary
Severity: High
Advisory: CVE-2023-6186
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-12-11
Source: https://osv.dev/vulnerability/CVE-2023-6186
Type: osv

## Details
Insufficient macro permission validation of The Document Foundation LibreOffice allows an attacker to execute built-in macros without warning.

In affected versions LibreOffice supports hyperlinks with macro or similar built-in command targets that can be executed when activated without warning the user.

## References
- https://lists.debian.org/debian-lts-announce/2023/12/msg00026.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/QB7UB6CTWQUDOE657OVVRSDYUY3IPBJG/
- https://www.debian.org/security/2023/dsa-5574
- https://www.libreoffice.org/about-us/security/advisories/cve-2023-6186
