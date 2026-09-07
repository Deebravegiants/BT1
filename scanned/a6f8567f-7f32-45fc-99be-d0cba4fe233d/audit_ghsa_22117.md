# [H] CakePHP allows method override parameters to bypass CSRF checks

## Summary
Severity: High
Advisory: GHSA-9pgx-pf36-w46r
CVE: CVE-2020-35239
CWE: CWE-352
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-9pgx-pf36-w46r
Type: github-advisory

## Affected
- Packagist: `cakephp/cakephp` — affected >=4.0.0 <4.0.10
- Packagist: `cakephp/cakephp` — affected >=4.1.0 <4.1.4

## Details
A vulnerability exists in CakePHP versions 4.0.x through 4.1.3. The CsrfProtectionMiddleware component allows method override parameters to bypass CSRF checks by changing the HTTP request method to an arbitrary string that is not in the list of request methods that CakePHP checks. Additionally, the route middleware does not verify that this overriden method (which can be an arbitrary string) is actually an HTTP method.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-35239
- https://bakery.cakephp.org/2020/12/07/cakephp_4010_released.html
- https://github.com/cakephp/cakephp
