# [H] CVE-2021-25634

## Summary
Severity: High
Advisory: CVE-2021-25634
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2021-10-12
Source: https://osv.dev/vulnerability/CVE-2021-25634
Type: osv

## Details
LibreOffice supports digital signatures of ODF documents and macros within documents, presenting visual aids that no alteration of the document occurred since the last signing and that the signature is valid. An Improper Certificate Validation vulnerability in LibreOffice allowed an attacker to modify a digitally signed ODF document to insert an additional signing time timestamp which LibreOffice would incorrectly present as a valid signature signed at the bogus signing time. This issue affects: The Document Foundation LibreOffice 7-0 versions prior to 7.0.6; 7-1 versions prior to 7.1.2.

## References
- https://www.libreoffice.org/about-us/security/advisories/CVE-2021-25634
- https://www.debian.org/security/2021/dsa-4988
