# [H] CVE-2022-26307

## Summary
Severity: High
Advisory: CVE-2022-26307
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-07-25
Source: https://osv.dev/vulnerability/CVE-2022-26307
Type: osv

## Details
LibreOffice supports the storage of passwords for web connections in the user’s configuration database. The stored passwords are encrypted with a single master key provided by the user. A flaw in LibreOffice existed where master key was poorly encoded resulting in weakening its entropy from 128 to 43 bits making the stored passwords vulerable to a brute force attack if an attacker has access to the users stored config. This issue affects: The Document Foundation LibreOffice 7.2 versions prior to 7.2.7; 7.3 versions prior to 7.3.3.

## References
- http://www.openwall.com/lists/oss-security/2022/08/13/2
- https://lists.debian.org/debian-lts-announce/2023/03/msg00022.html
- https://www.libreoffice.org/about-us/security/advisories/cve-2022-26307
