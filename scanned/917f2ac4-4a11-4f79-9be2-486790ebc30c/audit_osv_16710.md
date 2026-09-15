# [M] CVE-2019-9147

## Summary
Severity: Medium
Advisory: CVE-2019-9147
CVSS: 4.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N)
Published: 2019-07-09
Source: https://osv.dev/vulnerability/CVE-2019-9147
Type: osv

## Details
Mailvelope prior to 3.1.0 is vulnerable to a clickjacking attack against the settings page. As the settings page is intended to be accessible from web applications, the browser's extension isolation mechanisms are disabled (web_accessible_resources). Mailvelope implements additional measures to prevent web applications from directly embedding the settings page, but this mechanism can be bypassed.

## References
- https://www.bsi.bund.de/SharedDocs/Downloads/EN/BSI/Publications/Studies/Mailvelope_Extensions/Mailvelope_Extensions_pdf.html
- https://www.bsi.bund.de/SharedDocs/Downloads/EN/BSI/Publications/Studies/Mailvelope_Extensions/Mailvelope_Extensions_pdf.pdf?__blob=publicationFile&v=3
- https://github.com/mailvelope/mailvelope/blob/master/Changelog.md#v310
