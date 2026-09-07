# [M] Cross-site Scripting and Open Redirect in plone.app.contenttypes

## Summary
Severity: Medium
Advisory: GHSA-f7qw-5fgj-247x
CWE: CWE-601, CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-02-01
Source: https://github.com/advisories/GHSA-f7qw-5fgj-247x
Type: github-advisory

## Affected
- PyPI: `plone.app.contenttypes` — affected >=0 <2.2.3

## Details
### Impact
Plone is vulnerable to reflected cross site scripting and open redirect when an attacker can get a compromised version of the image_view_fullscreen page in a cache, for example in Varnish.
The technique is known as cache poisoning.
Any later visitor can get redirected when clicking on a link on this page.
Usually only anonymous users are affected, but this depends on your cache settings.

### Patches
New versions of plone.app.contenttypes have been released.
Version 2.2.3 works on Plone 5.2 and will be included in Plone 5.2.7.
Version 3.0.0a9 works on Plone 6 and will be included in Plone 6.0.0a3.

Note that the Products.CMFPlone package has the same problem in the 4.3 series.
In Plone 5.0-5.2, the default Products.ATContentTypes version has the same problem. See [advisory](https://github.com/plone/Products.ATContentTypes/security/advisories/GHSA-g4c2-ghfg-g5rh).
For all unpatched versions of the three packages, you can use the following workaround.

### Workaround
Make sure the image_view_fullscreen page is not stored in the cache.
In Plone:

* Login as Manager and go to Site Setup.
* Go to the 'Caching' control panel. If this does not exist, or 'Enable caching' is not checked, you should normally not be vulnerable.
* Click on the tab 'Caching operations'.
* Under 'Legacy template mappings' locate the ruleset 'Content item view'.
* From the last column ('Templates')  remove 'image_view_fullscreen'.
* Click on Save.

### Reporter
This vulnerability was responsibly disclosed to the Plone Security Team by Gustav Hansen, F-Secure Consulting. Thank you!

### For more information
If you have any questions or comments about this advisory, email us at [security@plone.org](mailto:security@plone.org)
This is also the correct address to use when you want to report a possible vulnerability.
See [our security report policy](https://plone.org/security/report).

## References
- https://github.com/plone/Products.ATContentTypes/security/advisories/GHSA-g4c2-ghfg-g5rh
- https://github.com/plone/plone.app.contenttypes/security/advisories/GHSA-f7qw-5fgj-247x
- https://github.com/plone/plone.app.contenttypes
