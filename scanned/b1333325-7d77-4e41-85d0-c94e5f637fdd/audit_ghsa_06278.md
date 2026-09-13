# [M] Wagtail: Improper restriction handling on descendant collections in Documents and Images API

## Summary
Severity: Medium
Advisory: GHSA-c2xx-cjmh-9q8f
CWE: CWE-280
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-08-20
Source: https://github.com/advisories/GHSA-c2xx-cjmh-9q8f
Type: github-advisory

## Affected
- PyPI: `wagtail` — affected >=0 <7.0.9
- PyPI: `wagtail` — affected >=7.1 <7.3.4
- PyPI: `wagtail` — affected >=7.4 <7.4.3
- PyPI: `wagtail` — affected >=8.0rc1 <8.0rc2

## Details
### Impact

The Documents and Images [API V2](https://docs.wagtail.org/en/stable/advanced_topics/api/index.html) incorrectly listed items in descendants of private collections, which should inherit the view restrictions defined on their ancestors. A user with access to the API could see the filename and name of documents and images in these descendant collections.

### Patches

Patched versions have been released as Wagtail 7.0.9, 7.3.4, 7.4.3 and 8.0rc2.

### Workarounds

Site owners using Wagtail's API can avoid the vulnerability by adding [authentication](https://docs.wagtail.org/en/stable/advanced_topics/api/v2/configuration.html#authentication) to the Documents and Images APIs.


### Acknowledgements

Many thanks to Ta Duc Thien for reporting this issue.

### For more information
If you have any questions or comments about this advisory:

* Visit Wagtail's [support channels](https://docs.wagtail.org/en/stable/support.html)
* Email us at [security@wagtail.org](mailto:security@wagtail.org) (view our [security policy](https://github.com/wagtail/wagtail/security/policy) for more information).

## References
- https://github.com/wagtail/wagtail/security/advisories/GHSA-c2xx-cjmh-9q8f
- https://github.com/wagtail/wagtail
