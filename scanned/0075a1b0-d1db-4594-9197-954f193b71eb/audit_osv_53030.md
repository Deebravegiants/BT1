# [H] CVE-2022-26306

## Summary
Severity: High
Advisory: CVE-2022-26306
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-07-25
Source: https://osv.dev/vulnerability/CVE-2022-26306
Type: osv

## Details
LibreOffice supports the storage of passwords for web connections in the user’s configuration database. The stored passwords are encrypted with a single master key provided by the user. A flaw in LibreOffice existed where the required initialization vector for encryption was always the same which weakens the security of the encryption making them vulnerable if an attacker has access to the user's configuration data. This issue affects: The Document Foundation LibreOffice 7.2 versions prior to 7.2.7; 7.3 versions prior to 7.3.1.

## References
- http://www.openwall.com/lists/oss-security/2022/08/13/1
- https://lists.debian.org/debian-lts-announce/2023/03/msg00022.html
- https://www.libreoffice.org/about-us/security/advisories/cve-2022-26306
