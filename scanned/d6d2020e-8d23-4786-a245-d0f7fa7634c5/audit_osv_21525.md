# [M] CVE-2021-43777

## Summary
Severity: Medium
Advisory: CVE-2021-43777
Aliases: GHSA-vhc7-w7r8-8m34
CVSS: 6.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N)
Published: 2021-11-24
Source: https://osv.dev/vulnerability/CVE-2021-43777
Type: osv

## Details
Redash is a package for data visualization and sharing. In Redash version 10.0 and prior, the implementation of Google Login (via OAuth) incorrectly uses the `state` parameter to pass the next URL to redirect the user to after login. The `state` parameter should be used for a Cross-Site Request Forgery (CSRF) token, not a static and easily predicted value. This vulnerability does not affect users who do not use Google Login for their instance of Redash. A patch in the `master` and `release/10.x.x` branches addresses this by replacing `Flask-Oauthlib` with `Authlib` which automatically provides and validates a CSRF token for the state variable. The new implementation stores the next URL on the user session object. As a workaround, one may disable Google Login to mitigate the vulnerability.

## References
- https://github.com/getredash/redash/security/advisories/GHSA-vhc7-w7r8-8m34
- https://github.com/getredash/redash/commit/da696ff7f84787cbf85967460fac52886cbe063e
