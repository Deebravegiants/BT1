# [H] Scrapy: S3DownloadHandler sends signed S3 requests over plaintext HTTP by default

## Summary
Severity: High
Advisory: CVE-2026-84366
Aliases: GHSA-76g3-c3x4-crvx, PYSEC-2026-3918
CVSS: 7.4 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-09-01
Source: https://osv.dev/vulnerability/CVE-2026-84366
Type: osv

## Details
Scrapy is a high-level web crawling and scraping framework for Python. Prior to 2.17.0, in scrapy/core/downloader/handlers/s3.py, Scrapy's S3DownloadHandler converts an S3-scheme bucket and key request into a plaintext HTTP request to the corresponding S3 endpoint unless request.meta["is_secure"] is explicitly enabled, then signs and sends the plaintext request with configured AWS credentials. A network attacker who can observe traffic between Scrapy and S3 can read the bucket and key path, AWS Authorization header, X-Amz-Security-Token when temporary credentials are used, S3 object contents, and S3 response headers. An active man-in-the-middle attacker can also modify the plaintext S3 response body, status code, and headers before Scrapy processes them, causing scraped-data poisoning, poisoned exports, HTTP cache poisoning when caching is enabled, or influence over later crawl targets through forged redirects or attacker-controlled links. Users making S3-scheme requests with AWS credentials are affected. This issue is fixed in version 2.17.0.

## References
- https://github.com/scrapy/scrapy/releases/tag/2.17.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/84xxx/CVE-2026-84366.json
- https://github.com/scrapy/scrapy/security/advisories/GHSA-76g3-c3x4-crvx
- https://nvd.nist.gov/vuln/detail/CVE-2026-84366
- https://github.com/scrapy/scrapy/commit/9523e1ec8c41fde265a26d14563d178b6f1ad04b
