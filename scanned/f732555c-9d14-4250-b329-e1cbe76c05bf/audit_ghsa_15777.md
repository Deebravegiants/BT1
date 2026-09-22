# [H] Wagtail regular expression denial-of-service via search query parsing

## Summary
Severity: High
Advisory: GHSA-jmp3-39vp-fwg8
CVE: CVE-2024-39317
CWE: CWE-1333
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-07-11
Source: https://github.com/advisories/GHSA-jmp3-39vp-fwg8
Type: github-advisory

## Affected
- PyPI: `wagtail` — affected >=6.0 <6.0.6
- PyPI: `wagtail` — affected >=6.1 <6.1.3
- PyPI: `wagtail` — affected >=2.0 <5.2.6

## Details
### Impact

A bug in Wagtail's [`parse_query_string`](https://docs.wagtail.org/en/stable/topics/search/searching.html#wagtailsearch-query-string-parsing) would result in it taking a long time to process suitably crafted inputs. When used to parse sufficiently long strings of characters without a space, `parse_query_string` would take an unexpectedly large amount of time to process, resulting in a denial of service.

In an initial Wagtail installation, the vulnerability can be exploited by any Wagtail admin user. It cannot be exploited by end users. If your Wagtail site has a custom search implementation which uses `parse_query_string`, it may be exploitable by other users (e.g. unauthenticated users).

### Patches

Patched versions have been released as Wagtail 5.2.6, 6.0.6 and 6.1.3.

This vulnerability affects all unpatched versions from Wagtail 2.0 onwards.

### Workarounds

Site owners who are unable to upgrade to a patched version can limit the length of search terms passed to `parse_query_string`. Whilst the performance characteristics will depend on your hosting environment, 1000 characters has been shown to still be fairly fast, without triggering this vulnerability.

No workaround is available for the Wagtail admin usage.

### Acknowledgements

Many thanks to [Jake Howard](https://github.com/RealOrangeOne) for reporting this issue.

### For more information
If you have any questions or comments about this advisory:

* Visit Wagtail's [support channels](https://docs.wagtail.io/en/stable/support.html)
* Email us at [security@wagtail.org](mailto:security@wagtail.org) (view our [security policy](https://github.com/wagtail/wagtail/security/policy) for more information).

## References
- https://github.com/wagtail/wagtail/security/advisories/GHSA-jmp3-39vp-fwg8
- https://nvd.nist.gov/vuln/detail/CVE-2024-39317
- https://github.com/wagtail/wagtail/commit/31b1e8532dfb1b70d8d37d22aff9cbde9109cdf2
- https://github.com/wagtail/wagtail/commit/3c941136f79c48446e3858df46e5b668d7f83797
- https://github.com/wagtail/wagtail/commit/b783c096b6d4fd2cfc05f9137a0be288850e99a2
- https://github.com/pypa/advisory-database/tree/main/vulns/wagtail/PYSEC-2024-86.yaml
- https://github.com/wagtail/wagtail
