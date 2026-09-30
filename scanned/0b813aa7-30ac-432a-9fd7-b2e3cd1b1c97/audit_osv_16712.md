# [M] CVE-2019-9149

## Summary
Severity: Medium
Advisory: CVE-2019-9149
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2019-07-09
Source: https://osv.dev/vulnerability/CVE-2019-9149
Type: osv

## Details
Mailvelope prior to 3.3.0 allows private key operations without user interaction via its client-API. By modifying an URL parameter in Mailvelope, an attacker is able to sign (and encrypt) arbitrary messages with Mailvelope, assuming the private key password is cached. A second vulnerability allows an attacker to decrypt an arbitrary message when the GnuPG backend is used in Mailvelope.

## References
- https://github.com/mailvelope/mailvelope/blob/master/Changelog.md#v330
- https://www.bsi.bund.de/SharedDocs/Downloads/EN/BSI/Publications/Studies/Mailvelope_Extensions/Mailvelope_Extensions_pdf.html
- https://www.bsi.bund.de/SharedDocs/Downloads/EN/BSI/Publications/Studies/Mailvelope_Extensions/Mailvelope_Extensions_pdf.pdf?__blob=publicationFile&v=3
