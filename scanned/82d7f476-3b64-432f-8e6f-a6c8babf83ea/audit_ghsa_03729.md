# [H] Cross-Site Request Forgery (CSRF) in hswebframework.web:hsweb-commons

## Summary
Severity: High
Advisory: GHSA-4rm3-4mq4-mfwr
CVE: CVE-2018-20595
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2019-01-04
Source: https://github.com/advisories/GHSA-4rm3-4mq4-mfwr
Type: github-advisory

## Affected
- Maven: `org.hswebframework.web:hsweb-commons` — affected >=0

## Details
A CSRF issue was discovered in web/authorization/oauth2/controller/OAuth2ClientController.java in hsweb 3.0.4 because the state parameter in the request is not compared with the state parameter in the session after user authentication is successful.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-20595
- https://github.com/hs-web/hsweb-framework/issues/107
- https://github.com/hs-web/hsweb-framework/commit/40929e9b0d336a26281a5ed2e0e721d54dd8d2f2
- https://github.com/advisories/GHSA-4rm3-4mq4-mfwr
- https://github.com/hs-web/hsweb-framework
