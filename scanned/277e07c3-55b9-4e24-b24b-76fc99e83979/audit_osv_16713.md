# [M] CVE-2019-9150

## Summary
Severity: Medium
Advisory: CVE-2019-9150
CVSS: 5.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2019-07-09
Source: https://osv.dev/vulnerability/CVE-2019-9150
Type: osv

## Details
Mailvelope prior to 3.3.0 does not require user interaction to import public keys shown on web page. This functionality can be tricked to either hide a key import from the user or obscure which key was imported.

## References
- https://www.bsi.bund.de/SharedDocs/Downloads/EN/BSI/Publications/Studies/Mailvelope_Extensions/Mailvelope_Extensions_pdf.html
- https://www.bsi.bund.de/SharedDocs/Downloads/EN/BSI/Publications/Studies/Mailvelope_Extensions/Mailvelope_Extensions_pdf.pdf?__blob=publicationFile&v=3
- https://github.com/mailvelope/mailvelope/blob/master/Changelog.md#v330
