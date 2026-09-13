# [H] Scrapy authorization header leakage on cross-domain redirect

## Summary
Severity: High
Advisory: GHSA-cw9j-q3vf-hrrv
CVE: CVE-2024-3574
CWE: CWE-200
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-02-15
Source: https://github.com/advisories/GHSA-cw9j-q3vf-hrrv
Type: github-advisory

## Affected
- PyPI: `scrapy` — affected >=2 <2.11.1
- PyPI: `scrapy` — affected >=0 <1.8.4

## Details
### Impact

When you send a request with the `Authorization` header to one domain, and the response asks to redirect to a different domain, Scrapy’s built-in redirect middleware creates a follow-up redirect request that keeps the original `Authorization` header, leaking its content to that second domain.

The [right behavior](https://fetch.spec.whatwg.org/#ref-for-cors-non-wildcard-request-header-name) would be to drop the `Authorization` header instead, in this scenario.

### Patches

Upgrade to Scrapy 2.11.1.

If you are using Scrapy 1.8 or a lower version, and upgrading to Scrapy 2.11.1 is not an option, you may upgrade to Scrapy 1.8.4 instead.

### Workarounds

If you cannot upgrade, make sure that you are not using the `Authentication` header, either directly or through some third-party plugin.

If you need to use that header in some requests, add `"dont_redirect": True` to the `request.meta` dictionary of those requests to disable following redirects for them.

If you need to keep (same domain) redirect support on those requests, make sure you trust the target website not to redirect your requests to a different domain.

### Acknowledgements

This security issue was reported by @ranjit-git  [through huntr.com](https://huntr.com/bounties/49974321-2718-43e3-a152-62b16eed72a9/).

## References
- https://github.com/scrapy/scrapy/security/advisories/GHSA-cw9j-q3vf-hrrv
- https://nvd.nist.gov/vuln/detail/CVE-2024-3574
- https://github.com/scrapy/scrapy/commit/ee7bd9d217fc126063575d5649f00bdeeca2faae
- https://github.com/scrapy/scrapy
- https://huntr.com/bounties/49974321-2718-43e3-a152-62b16eed72a9
