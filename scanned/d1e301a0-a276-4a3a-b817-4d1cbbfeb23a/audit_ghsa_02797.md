# [H] Splash authentication credentials potentially leaked to target websites 

## Summary
Severity: High
Advisory: GHSA-823f-cwm9-4g74
CVE: CVE-2021-41124
CWE: CWE-200
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2021-10-06
Source: https://github.com/advisories/GHSA-823f-cwm9-4g74
Type: github-advisory

## Affected
- PyPI: `scrapy-splash` — affected >=0 <0.8.0

## Details
### Impact

If you use [`HttpAuthMiddleware`](http://doc.scrapy.org/en/latest/topics/downloader-middleware.html#module-scrapy.downloadermiddlewares.httpauth) (i.e. the `http_user` and `http_pass` spider attributes) for Splash authentication, any non-Splash request will expose your credentials to the request target. This includes `robots.txt` requests sent by Scrapy when the `ROBOTSTXT_OBEY` setting is set to `True`.

### Patches

Upgrade to scrapy-splash 0.8.0 and use the new `SPLASH_USER` and `SPLASH_PASS` settings instead to set your Splash authentication credentials safely.

### Workarounds

If you cannot upgrade, set your Splash request credentials on a per-request basis, [using the `splash_headers` request parameter](https://github.com/scrapy-plugins/scrapy-splash/tree/0.8.x#http-basic-auth), instead of defining them globally using the [`HttpAuthMiddleware`](http://doc.scrapy.org/en/latest/topics/downloader-middleware.html#module-scrapy.downloadermiddlewares.httpauth).

Alternatively, make sure all your requests go through Splash. That includes disabling the [robots.txt middleware](https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#topics-dlmw-robots).

### For more information
If you have any questions or comments about this advisory:
* [Open an issue](https://github.com/scrapy-plugins/scrapy-splash/issues)
* [Email us](mailto:opensource@zyte.com)

## References
- https://github.com/scrapy-plugins/scrapy-splash/security/advisories/GHSA-823f-cwm9-4g74
- https://nvd.nist.gov/vuln/detail/CVE-2021-41124
- https://github.com/scrapy-plugins/scrapy-splash/commit/2b253e57fe64ec575079c8cdc99fe2013502ea31
- https://github.com/pypa/advisory-database/tree/main/vulns/scrapy-splash/PYSEC-2021-364.yaml
- https://github.com/scrapy-plugins/scrapy-splash
- https://github.com/scrapy-plugins/scrapy-splash/releases/tag/0.8.0
