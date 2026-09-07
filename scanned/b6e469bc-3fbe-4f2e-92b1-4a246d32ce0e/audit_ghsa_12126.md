# [M] Products.isurlinportal has possible open redirect when using more than 2 forward slashes

## Summary
Severity: Medium
Advisory: GHSA-43gx-6gv6-3jcp
CVE: CVE-2026-28413
CWE: CWE-601
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-03-02
Source: https://github.com/advisories/GHSA-43gx-6gv6-3jcp
Type: github-advisory

## Affected
- PyPI: `Products.isurlinportal` — affected >=4.0.0a1 <4.0.0
- PyPI: `Products.isurlinportal` — affected >=3.0.0 <3.1.0
- PyPI: `Products.isurlinportal` — affected >=0 <2.1.0
- PyPI: `products-isurlinportal` — affected >=0 <2.1.0
- PyPI: `products-isurlinportal` — affected >=3.0.0 <3.1.0

## Details
### Impact
A url `/login?came_from=////evil.example` may redirect to an external website after login.

Standard Plone is not affected, but if you have customised the login, for example with add-ons, you might be affected. You can try the url to check if you are affected or not.

### Patches
The problem has been patched in `Products.isurlinportal`.

* Plone 6.2: upgrade to `Products.isurlinportal` 4.0.0.
* Plone 6.1: upgrade to `Products.isurlinportal` 3.1.0.
* Plone 6.0: upgrade to `Products.isurlinportal` 2.1.0.
* Older Plone versions don't have security support anymore.

### Workarounds
There are no known workarounds.

### Background
When you are anonymous and land on a page that requires a login, Plone sends you to the login form. After successful login, Plone redirects you back to the page you came from.  Various other forms and pages have a similar system.

This could get abused by an attacker to trick Plone into redirecting to a different website. Plone checks the page that would be redirected to. It is only accepted if it is within the Plone site domain or part of a different trusted domain.

The main check for this is in the `Products.isurlinportal` package. A lot of potentially malicious urls are already safely rejected, but here a loop hole was found.

This was discovered during a penetration test by the CERT-EU Team.

## References
- https://github.com/plone/Products.isurlinportal/security/advisories/GHSA-43gx-6gv6-3jcp
- https://nvd.nist.gov/vuln/detail/CVE-2026-28413
- https://github.com/plone/Products.isurlinportal
- https://github.com/pypa/advisory-database/tree/main/vulns/products-isurlinportal/PYSEC-2026-112.yaml
