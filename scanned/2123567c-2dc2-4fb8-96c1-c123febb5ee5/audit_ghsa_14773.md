# [M] Vulnerable embedded jQuery Version

## Summary
Severity: Medium
Advisory: GHSA-jmh9-6rjq-gjh9
Ecosystem: Packagist
Published: 2024-06-05
Source: https://github.com/advisories/GHSA-jmh9-6rjq-gjh9
Type: github-advisory

## Affected
- Packagist: `pimcore/admin-ui-classic-bundle` — affected >=0 <1.4.3

## Details
### Summary
PIMCore uses the JavaScript library jQuery in version 3.4.1. This version is vulnerable to cross-site-scripting (XSS).

### Details
In jQuery versions greater than or equal to 1.0.3 and before 3.5.0, passing HTML containing elements from untrusted sources - even after sanitizing it to one of jQuery's DOM manipulation methods (i.e. .html(), .append(), and others) may execute untrusted code. This problem is patched in jQuery 3.5.0.

Publish Date: 2020-04-29

URL:= https://security.snyk.io/package/npm/jquery/3.4.1

## References
- https://github.com/pimcore/admin-ui-classic-bundle/security/advisories/GHSA-jmh9-6rjq-gjh9
- https://github.com/pimcore/admin-ui-classic-bundle
