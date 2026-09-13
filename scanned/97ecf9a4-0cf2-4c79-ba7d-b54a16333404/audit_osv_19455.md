# [M] CVE-2021-21336

## Summary
Severity: Medium
Advisory: CVE-2021-21336
Aliases: GHSA-p75f-g7gx-2r7p, PYSEC-2021-44
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-03-08
Source: https://osv.dev/vulnerability/CVE-2021-21336
Type: osv

## Details
Products.PluggableAuthService is a pluggable Zope authentication and authorization framework. In Products.PluggableAuthService before version 2.6.0 there is an information disclosure vulnerability - everyone can list the names of roles defined in the ZODB Role Manager plugin if the site uses this plugin. The problem has been fixed in version 2.6.0. Depending on how you have installed Products.PluggableAuthService, you should change the buildout version pin to 2.6.0 and re-run the buildout, or if you used pip simply do `pip install "Products.PluggableAuthService>=2.6.0"`.

## References
- http://www.openwall.com/lists/oss-security/2021/05/21/1
- http://www.openwall.com/lists/oss-security/2021/05/22/1
- https://github.com/zopefoundation/Products.PluggableAuthService/security/advisories/GHSA-p75f-g7gx-2r7p
- https://github.com/zopefoundation/Products.PluggableAuthService/commit/2dad81128250cb2e5d950cddc9d3c0314a80b4bb
- https://pypi.org/project/Products.PluggableAuthService/
