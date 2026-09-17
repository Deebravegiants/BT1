# [M] Scrapy's redirects ignoring scheme-specific proxy settings

## Summary
Severity: Medium
Advisory: GHSA-jm3v-qxmh-hxwv
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-05-14
Source: https://github.com/advisories/GHSA-jm3v-qxmh-hxwv
Type: github-advisory

## Affected
- PyPI: `Scrapy` — affected >=0 <2.11.2

## Details
### Impact

When using system proxy settings, which are scheme-specific (i.e. specific to `http://` or `https://` URLs), Scrapy was not accounting for scheme changes during redirects.

For example, an HTTP request would use the proxy configured for HTTP and, when redirected to an HTTPS URL, the new HTTPS request would still use the proxy configured for HTTP instead of switching to the proxy configured for HTTPS. Same the other way around.

If you have different proxy configurations for HTTP and HTTPS in your system for security reasons (e.g., maybe you don’t want one of your proxy providers to be aware of the URLs that you visit with the other one), this would be a security issue.

### Patches

Upgrade to Scrapy 2.11.2.

### Workarounds

Replace the built-in retry middlewares (`RedirectMiddleware` and `MetaRefreshMiddleware`) and the `HttpProxyMiddleware` middleware with custom ones that implement the fix from Scrapy 2.11.2, and verify that they work as intended.

### References

This security issue was reported by @redapple at https://github.com/scrapy/scrapy/issues/767.

## References
- https://github.com/scrapy/scrapy/security/advisories/GHSA-jm3v-qxmh-hxwv
- https://github.com/scrapy/scrapy/issues/767
- https://github.com/scrapy/scrapy/commit/1d0502f25bbe55a22899af915623fda1aaeb9dd8
- https://github.com/scrapy/scrapy
