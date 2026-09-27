# [H] Scrapy decompression bomb vulnerability

## Summary
Severity: High
Advisory: GHSA-7j7m-v7m3-jqm7
CVE: CVE-2024-3572
CWE: CWE-409
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-02-16
Source: https://github.com/advisories/GHSA-7j7m-v7m3-jqm7
Type: github-advisory

## Affected
- PyPI: `scrapy` — affected >=2.0.0 <2.11.1
- PyPI: `scrapy` — affected >=0 <1.8.4

## Details
### Impact

Scrapy limits allowed response sizes by default through the [`DOWNLOAD_MAXSIZE`](https://docs.scrapy.org/en/latest/topics/settings.html#download-maxsize) and [`DOWNLOAD_WARNSIZE`](https://docs.scrapy.org/en/latest/topics/settings.html#download-warnsize) settings.

However, those limits were only being enforced during the download of the raw, usually-compressed response bodies, and not during decompression, making Scrapy vulnerable to [decompression bombs](https://cwe.mitre.org/data/definitions/409.html).

A malicious website being scraped could send a small response that, on decompression, could exhaust the memory available to the Scrapy process, potentially affecting any other process sharing that memory, and affecting disk usage in case of uncompressed response caching.

### Patches

Upgrade to Scrapy 2.11.1.

If you are using Scrapy 1.8 or a lower version, and upgrading to Scrapy 2.11.1 is not an option, you may upgrade to Scrapy 1.8.4 instead.

### Workarounds

There is no easy workaround.

Disabling HTTP decompression altogether is impractical, as HTTP compression is a rather common practice.

However, it is technically possible to manually backport the 2.11.1 or 1.8.4 fix, replacing the corresponding components of an unpatched version of Scrapy with patched versions copied into your own code.

### Acknowledgements

This security issue was reported by @dmandefy  [through huntr.com](https://huntr.com/bounties/c4a0fac9-0c5a-4718-9ee4-2d06d58adabb/).

## References
- https://github.com/scrapy/scrapy/security/advisories/GHSA-7j7m-v7m3-jqm7
- https://nvd.nist.gov/vuln/detail/CVE-2024-3572
- https://github.com/scrapy/scrapy/commit/71b8741e3607cfda2833c7624d4ada87071aa8e5
- https://github.com/scrapy/scrapy/commit/809bfac4890f75fc73607318a04d2ccba71b3d9f
- https://docs.scrapy.org/en/latest/news.html#scrapy-2-11-1-2024-02-14
- https://github.com/scrapy/scrapy
- https://huntr.com/bounties/c4a0fac9-0c5a-4718-9ee4-2d06d58adabb
