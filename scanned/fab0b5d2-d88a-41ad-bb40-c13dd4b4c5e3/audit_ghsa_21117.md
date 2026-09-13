# [M] Scrapy before 2.6.2 and 1.8.3 vulnerable to one proxy sending credentials to another

## Summary
Severity: Medium
Advisory: GHSA-9x8m-2xpf-crp3
Ecosystem: PyPI
Published: 2022-07-29
Source: https://github.com/advisories/GHSA-9x8m-2xpf-crp3
Type: github-advisory

## Affected
- PyPI: `scrapy` — affected >=0 <1.8.3
- PyPI: `scrapy` — affected >=2.0.0 <2.6.2

## Details
### Impact

When the [built-in HTTP proxy downloader middleware](https://docs.scrapy.org/en/2.6/topics/downloader-middleware.html#module-scrapy.downloadermiddlewares.httpproxy) processes a request with `proxy` metadata, and that `proxy` metadata includes proxy credentials, the built-in HTTP proxy downloader middleware sets the `Proxy-Authentication` header, but only if that header is not already set.

There are third-party proxy-rotation downloader middlewares that set different `proxy` metadata every time they process a request.

Because of request retries and redirects, the same request can be processed by downloader middlewares more than once, including both the built-in HTTP proxy downloader middleware and any third-party proxy-rotation downloader middleware.

These third-party proxy-rotation downloader middlewares could change the `proxy` metadata of a request to a new value, but fail to remove the `Proxy-Authentication` header from the previous value of the `proxy` metadata, causing the credentials of one proxy to be leaked to a different proxy.

If you rotate proxies from different proxy providers, and any of those proxies requires credentials, you are affected, unless you are handling proxy rotation as described under **Workarounds** below. If you use a third-party downloader middleware for proxy rotation, the same applies to that downloader middleware, and installing a patched version of Scrapy may not be enough; patching that downloader middlware may be necessary as well.

### Patches

Upgrade to Scrapy 2.6.2.

If you are using Scrapy 1.8 or a lower version, and upgrading to Scrapy 2.6.2 is not an option, you may upgrade to Scrapy 1.8.3 instead.

### Workarounds

If you cannot upgrade, make sure that any code that changes the value of the `proxy` request meta also removes the `Proxy-Authorization` header from the request if present.

### For more information

If you have any questions or comments about this advisory:
* [Open an issue](https://github.com/scrapy/scrapy/issues)
* [Email us](mailto:opensource@zyte.com)

## References
- https://github.com/scrapy/scrapy/security/advisories/GHSA-9x8m-2xpf-crp3
- https://github.com/scrapy/scrapy/commit/af7dd16d8ded3e6cb2946603688f4f4a5212e80f
- https://github.com/scrapy/scrapy
