# [M] URL Redirection to Untrusted Site ('Open Redirect') in Products.PluggableAuthService

## Summary
Severity: Medium
Advisory: GHSA-p44j-xrqg-4xrr
CVE: CVE-2021-21337
CWE: CWE-601
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2021-03-08
Source: https://github.com/advisories/GHSA-p44j-xrqg-4xrr
Type: github-advisory

## Affected
- PyPI: `Products.PluggableAuthService` — affected >=0 <2.6.1

## Details
### Impact
_What kind of vulnerability is it? Who is impacted?_

Open redirect vulnerability - a maliciously crafted link to the login form and login functionality could redirect the browser to a different website.

### Patches
_Has the problem been patched? What versions should users upgrade to?_

The problem has been fixed in version 2.6.1. Depending on how you have installed Products.PluggableAuthService, you should change the buildout version pin to `2.6.1`  and re-run the buildout, or if you used `pip` simply do `pip install "Products.PluggableAuthService>=2.6.1"`

### Workarounds
_Is there a way for users to fix or remediate the vulnerability without upgrading?_

There is no workaround. Users are encouraged to upgrade.

### References
_Are there any links users can visit to find out more?_

- [GHSA-p44j-xrqg-4xrr](https://github.com/zopefoundation/Products.PluggableAuthService/security/advisories/GHSA-p44j-xrqg-4xrr)
- [Products.PluggableAuthService on PyPI](https://pypi.org/project/Products.PluggableAuthService/)
- [OWASP page on open redirects](https://cheatsheetseries.owasp.org/cheatsheets/Unvalidated_Redirects_and_Forwards_Cheat_Sheet.html)

### For more information
If you have any questions or comments about this advisory:
* Open an issue in the [Products.PluggableAuthService issue tracker](https://github.com/zopefoundation/Products.PluggableAuthService/issues)
* Email us at [security@plone.org](mailto:security@plone.org)

## References
- https://github.com/zopefoundation/Products.PluggableAuthService/security/advisories/GHSA-p44j-xrqg-4xrr
- https://nvd.nist.gov/vuln/detail/CVE-2021-21337
- https://github.com/zopefoundation/Products.PluggableAuthService/commit/7eead067898852ebd3e0f143bc51295928528dfa
- https://github.com/pypa/advisory-database/tree/main/vulns/products-pluggableauthservice/PYSEC-2021-45.yaml
- https://github.com/zopefoundation/Products.PluggableAuthService
- https://pypi.org/project/Products.PluggableAuthService
- http://packetstormsecurity.com/files/162911/Products.PluggableAuthService-2.6.0-Open-Redirect.html
