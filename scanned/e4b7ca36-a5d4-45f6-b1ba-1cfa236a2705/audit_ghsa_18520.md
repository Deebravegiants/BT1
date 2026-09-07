# [M] Umbraco Delivery API allows for cached requests to be returned with an invalid API key

## Summary
Severity: Medium
Advisory: GHSA-75vq-qvhr-7ffr
CVE: CVE-2025-54425
CWE: CWE-200
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-07-29
Source: https://github.com/advisories/GHSA-75vq-qvhr-7ffr
Type: github-advisory

## Affected
- NuGet: `Umbraco.Cms.Api.Delivery` — affected >=13.0.0 <13.9.3
- NuGet: `Umbraco.Cms.Api.Delivery` — affected >=15.0.0 <15.4.4
- NuGet: `Umbraco.Cms.Api.Delivery` — affected >=16.0.0 <16.1.1

## Details
### Impact
Umbraco's [content delivery API](https://docs.umbraco.com/umbraco-cms/reference/content-delivery-api) can be restricted from public access such that an API key must be provided in a header to authorize the request.

It's also possible to configure output caching, such that the delivery API outputs will be cached for a period of time, improving performance.

There's an issue when these two things are used together though in that the caching doesn't vary by the header that contains the API key.  As such it's possible for a user without a valid API key to retrieve a response for a given path and query if it has recently been requested and cached by request with a valid key.

### Patches
Patches will be available in 13.9.3, 15.4.4 and 16.1.1.

### Workarounds
Workaround is to remove or reduce the time period of the output caching or to provide other restrictions to access the delivery API such as by IP.

### References
Content delivery API documentation: https://docs.umbraco.com/umbraco-cms/reference/content-delivery-api

## References
- https://github.com/umbraco/Umbraco-CMS/security/advisories/GHSA-75vq-qvhr-7ffr
- https://nvd.nist.gov/vuln/detail/CVE-2025-54425
- https://github.com/umbraco/Umbraco-CMS/commit/7e82c258eebaa595eadc9b000461e27d02bc030e
- https://github.com/umbraco/Umbraco-CMS/commit/9f37db18d11c8ba4e3ecdeb35291af30ebee7cd0
- https://github.com/umbraco/Umbraco-CMS/commit/da43086017e1e318f6b5373391d78421efebce3a
- https://docs.umbraco.com/umbraco-cms/reference/content-delivery-api
- https://github.com/umbraco/Umbraco-CMS
