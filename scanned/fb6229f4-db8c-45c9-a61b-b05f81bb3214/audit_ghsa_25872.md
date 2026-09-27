# [M] Scrapy cookie-setting is not restricted based on the public suffix list

## Summary
Severity: Medium
Advisory: GHSA-mfjm-vh54-3f96
Ecosystem: PyPI
Published: 2022-03-01
Source: https://github.com/advisories/GHSA-mfjm-vh54-3f96
Type: github-advisory

## Affected
- PyPI: `scrapy` — affected >=0 <1.8.2
- PyPI: `scrapy` — affected >=2.0.0 <2.6.0

## Details
### Impact

Responses from domain names whose public domain name suffix contains 1 or more periods (e.g. responses from `example.co.uk`, given its public domain name suffix is `co.uk`) are able to set cookies that are included in requests to any other domain sharing the same domain name suffix.

### Patches

Upgrade to Scrapy 2.6.0, which restricts cookies with their domain set to any of those in the [public suffix list](https://publicsuffix.org/).

If you are using Scrapy 1.8 or a lower version, and upgrading to Scrapy 2.6.0 is not an option, you may upgrade to Scrapy 1.8.2 instead.

### Workarounds

The only workaround for unpatched versions of Scrapy is to [disable cookies altogether](https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#std-setting-COOKIES_ENABLED), or [limit target domains](https://docs.scrapy.org/en/latest/topics/spiders.html#scrapy.spiders.Spider.allowed_domains) to a subset that does not include domain names with one of the public domain suffixes affected (those with 1 or more periods).

### References
* https://publicsuffix.org/

### For more information

If you have any questions or comments about this advisory:
* [Open an issue](https://github.com/scrapy/scrapy/issues)
* [Email us](mailto:opensource@zyte.com)

## References
- https://github.com/scrapy/scrapy/security/advisories/GHSA-mfjm-vh54-3f96
- https://github.com/scrapy/scrapy/commit/e865c4430e58a4faa0e0766b23830f8423d6167a
- https://github.com/scrapy/scrapy
