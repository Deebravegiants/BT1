# [M] CVE-2019-9148

## Summary
Severity: Medium
Advisory: CVE-2019-9148
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N)
Published: 2019-07-09
Source: https://osv.dev/vulnerability/CVE-2019-9148
Type: osv

## Details
Mailvelope prior to 3.3.0 accepts or operates with invalid PGP public keys: Mailvelope allows importing keys that contain users without a valid self-certification. Keys that are obviously invalid are not rejected during import. An attacker that is able to get a victim to import a manipulated key could claim to have signed a message that originates from another person.

## References
- https://github.com/mailvelope/mailvelope/blob/master/Changelog.md#v330
- https://www.bsi.bund.de/SharedDocs/Downloads/EN/BSI/Publications/Studies/Mailvelope_Extensions/Mailvelope_Extensions_pdf.html
- https://www.bsi.bund.de/SharedDocs/Downloads/EN/BSI/Publications/Studies/Mailvelope_Extensions/Mailvelope_Extensions_pdf.pdf?__blob=publicationFile&v=3
