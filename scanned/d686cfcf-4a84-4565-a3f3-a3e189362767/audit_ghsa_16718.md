# [M] Scrapy leaks the authorization header on same-domain but cross-origin redirects

## Summary
Severity: Medium
Advisory: GHSA-4qqq-9vqf-3h3f
CVE: CVE-2024-1968
CWE: CWE-200
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-05-14
Source: https://github.com/advisories/GHSA-4qqq-9vqf-3h3f
Type: github-advisory

## Affected
- PyPI: `Scrapy` — affected >=0 <2.11.2

## Details
### Impact

Since version 2.11.1, Scrapy drops the `Authorization` header when a request is redirected to a different domain. However, it keeps the header if the domain remains the same but the scheme (http/https) or the port change, all scenarios where the header should also be dropped.

In the context of a man-in-the-middle attack, this could be used to get access to the value of that `Authorization` header

### Patches

Upgrade to Scrapy 2.11.2.

### Workarounds

There is no easy workaround for unpatched versions of Scrapy. You can replace the built-in redirect middlewares with custom ones patched for this issue, but you have to patch them yourself, manually.

### References

This security issue was reported and fixed by @szarny at https://huntr.com/bounties/27f6a021-a891-446a-ada5-0226d619dd1a/.

## References
- https://github.com/scrapy/scrapy/security/advisories/GHSA-4qqq-9vqf-3h3f
- https://github.com/scrapy/scrapy/commit/1d0502f25bbe55a22899af915623fda1aaeb9dd8
- https://github.com/scrapy/scrapy
- https://huntr.com/bounties/27f6a021-a891-446a-ada5-0226d619dd1a
