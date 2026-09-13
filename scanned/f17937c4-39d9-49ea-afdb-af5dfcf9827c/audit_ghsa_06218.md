# [M] django CMS: Page cache ignores plugin-declared Vary headers (disclosure & poisoning)

## Summary
Severity: Medium
Advisory: GHSA-fwjf-m4qw-9f2x
CVE: CVE-2026-54625
CWE: CWE-349, CWE-524
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-08-24
Source: https://github.com/advisories/GHSA-fwjf-m4qw-9f2x
Type: github-advisory

## Affected
- PyPI: `django-cms` — affected >=0 <5.0.8

## Details
### Summary
The CMS page cache key ignores the request headers that plugins declare via `get_vary_cache_on()`. The header is added to the response `Vary` header, but the CMS's own cache key does not incorporate the header values, so the first visitor's variant is served to all subsequent visitors regardless of their header values.

### Details
`_page_cache_key` (in `cms/cache/page.py`) keys only on cache prefix, site, language, path and timezone. `set_page_cache` collects the plugin-declared vary headers and calls `patch_vary_headers(response, ...)` (affecting only the emitted `Vary` header), but stores and retrieves the cached page under the header-agnostic key. `get_page_cache` therefore returns whichever variant was cached first.

### Impact
- **Information disclosure:** when a plugin varies its output on a request  header (e.g. `Country-Code`), the variant rendered for the first anonymous visitor is served to everyone until the entry expires, leaking request-specific content across users.
- **Cache poisoning:** an unauthenticated attacker can prime the anonymous page cache with content rendered from attacker-chosen header values, which is then served to subsequent visitors.

Applies only when `CMS_PAGE_CACHE` is enabled and at least one plugin implements `get_vary_cache_on()`.

### Patches
Fixed in 5.0.8: the page cache now folds the request's values implements `get_vary_cache_on()`.

### Patches
Fixed in 5.0.8: the page cache now folds the request's values for plugin-declared vary headers into the content key. The set of vary headers is persisted on write and looked up first on read (mirroring Django's  `learn_cache_key`/`get_cache_key`); a missing header-list entry degrades to a cache miss, never a wrong-variant hit.

### Workarounds
Disable `CMS_PAGE_CACHE`, or avoid plugins that rely on `get_vary_cache_on()`, until upgraded.

### Credits
Reported by the security team at the University of Sydney ([@reporter]).

## References
- https://github.com/django-cms/django-cms/security/advisories/GHSA-fwjf-m4qw-9f2x
- https://nvd.nist.gov/vuln/detail/CVE-2026-54625
- https://github.com/django-cms/django-cms/pull/8646
- https://github.com/django-cms/django-cms/pull/8647
- https://github.com/django-cms/django-cms/commit/8758714b865ffa79c6bcd0e5c503958ea48885aa
- https://github.com/django-cms/django-cms/commit/d5dc1efa18d157445491c4b12c2dd1efd56f439f
- https://github.com/django-cms/django-cms
- https://github.com/django-cms/django-cms/releases/tag/5.0.8
- https://github.com/django-cms/django-cms/releases/tag/5.1.0
