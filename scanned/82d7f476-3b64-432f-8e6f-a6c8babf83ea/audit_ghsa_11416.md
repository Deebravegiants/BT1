# [H] Scrapy: Arbitrary Module Import via Referrer-Policy Header in RefererMiddleware

## Summary
Severity: High
Advisory: GHSA-cwxj-rr6w-m6w7
CWE: CWE-470
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-03-13
Source: https://github.com/advisories/GHSA-cwxj-rr6w-m6w7
Type: github-advisory

## Affected
- PyPI: `Scrapy` — affected >=1.4.0 <2.14.2

## Details
### Impact

Since version 1.4.0, Scrapy respects the `Referrer-Policy` response header to decide whether and how to set a `Referer` header on follow-up requests.

If the header value looked like a valid Python import path, Scrapy would import the referenced object and call it, assuming it referred to a referrer policy class (for example, `scrapy.spidermiddlewares.referer.DefaultReferrerPolicy`) and attempting to instantiate it to handle the `Referer` header.

A malicious site could exploit this by setting `Referrer-Policy` to a path such as `sys.exit`, causing Scrapy to import and execute it and potentially terminate the process.

### Patches

Upgrade to Scrapy 2.14.2 (or later).

### Workarounds

If you cannot upgrade to Scrapy 2.14.2, consider the following mitigations.

- **Disable the middleware:** If you don't need the `Referer` header on follow-up requests, set [`REFERER_ENABLED`](https://docs.scrapy.org/en/latest/topics/spider-middleware.html#referer-enabled) to `False`.
- **Set headers manually:** If you do need a `Referer`, disable the middleware and set the header explicitly on the requests that require it.
- **Set `referrer_policy` in request metadata:** If disabling the middleware is not viable, set the [`referrer_policy`](https://docs.scrapy.org/en/latest/topics/spider-middleware.html#referrer-policy) request meta key on all requests to prevent evaluating preceding responses' `Referrer-Policy`. For example:

```python
Request(
    url,
    meta={
        "referrer_policy": "scrapy.spidermiddlewares.referer.DefaultReferrerPolicy",
    },
)
```

Instead of editing requests individually, you can:

- implement a custom [spider middleware](https://docs.scrapy.org/en/latest/topics/spider-middleware.html) that runs before the built-in referrer policy middleware and sets the `referrer_policy` meta key; or
- set the meta key in start requests and use the [scrapy-sticky-meta-params](https://github.com/heylouiz/scrapy-sticky-meta-params) plugin to propagate it to follow-up requests.

If you want to continue respecting legitimate `Referrer-Policy` headers while protecting against malicious ones, disable the built-in referrer policy middleware by setting it to `None` in [`SPIDER_MIDDLEWARES`](https://docs.scrapy.org/en/latest/topics/settings.html#std-setting-SPIDER_MIDDLEWARES) and replace it with the fixed implementation from Scrapy 2.14.2.

If the Scrapy 2.14.2 implementation is incompatible with your project (for example, because your Scrapy version is older), copy the corresponding middleware from your Scrapy version, apply the same patch, and use that as a replacement.

## References
- https://github.com/scrapy/scrapy/security/advisories/GHSA-cwxj-rr6w-m6w7
- https://github.com/scrapy/scrapy/commit/945b787a263586cb5803c01c6da57daad8997ae5
- https://github.com/scrapy/scrapy
