# [M] CVE-2020-12801

## Summary
Severity: Medium
Advisory: CVE-2020-12801
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2020-05-18
Source: https://osv.dev/vulnerability/CVE-2020-12801
Type: osv

## Details
If LibreOffice has an encrypted document open and crashes, that document is auto-saved encrypted. On restart, LibreOffice offers to restore the document and prompts for the password to decrypt it. If the recovery is successful, and if the file format of the recovered document was not LibreOffice's default ODF file format, then affected versions of LibreOffice default that subsequent saves of the document are unencrypted. This may lead to a user accidentally saving a MSOffice file format document unencrypted while believing it to be encrypted. This issue affects: LibreOffice 6-3 series versions prior to 6.3.6; 6-4 series versions prior to 6.4.3.

## References
- https://lists.debian.org/debian-lts-announce/2023/12/msg00026.html
- http://lists.opensuse.org/opensuse-security-announce/2020-06/msg00011.html
- https://www.libreoffice.org/about-us/security/advisories/CVE-2020-12801
