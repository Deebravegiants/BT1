# [H] mailcow-dockerized critical information misrepresentation can lead to phishing attacks through Swagger UI

## Summary
Severity: High
Advisory: CVE-2022-39258
Aliases: GHSA-vjgf-cp5p-wm45
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N)
Published: 2022-09-27
Source: https://osv.dev/vulnerability/CVE-2022-39258
Type: osv

## Details
mailcow is a mailserver suite. A vulnerability innversions prior to 2022-09 allows an attacker to craft a custom Swagger API template to spoof Authorize links. This could redirect a victim to an attacker controller place to steal Swagger authorization credentials or create a phishing page to steal other information. The issue has been fixed with the 2022-09 mailcow Mootember Update. As a workaround, one may delete the Swapper API Documentation from their e-mail server.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/39xxx/CVE-2022-39258.json
- https://github.com/mailcow/mailcow-dockerized/security/advisories/GHSA-vjgf-cp5p-wm45
- https://nvd.nist.gov/vuln/detail/CVE-2022-39258
- https://github.com/mailcow/mailcow-dockerized/pull/4766
