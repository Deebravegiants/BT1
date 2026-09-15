# [H] Scrapy is vulnerable to a denial of service (DoS) attack due to flaws in brotli decompression implementation

## Summary
Severity: High
Advisory: GHSA-2qfp-q593-8484
CVE: CVE-2025-6176
CWE: CWE-400
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-10-31
Source: https://github.com/advisories/GHSA-2qfp-q593-8484
Type: github-advisory

## Affected
- PyPI: `brotli` — affected >=0 <1.2.0
- PyPI: `Scrapy` — affected >=0 <2.13.4

## Details
Scrapy versions up to 2.13.3 are vulnerable to a denial of service (DoS) attack due to a flaw in its brotli decompression implementation. The protection mechanism against decompression bombs fails to mitigate the brotli variant, allowing remote servers to crash clients with less than 80GB of available memory. This occurs because brotli can achieve extremely high compression ratios for zero-filled data, leading to excessive memory consumption during decompression. Mitigation for this vulnerability needs security enhancement added in brotli v1.2.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-6176
- https://github.com/google/brotli/issues/1327
- https://github.com/google/brotli/issues/1375
- https://github.com/google/brotli/pull/1234
- https://github.com/scrapy/scrapy/pull/7134
- https://github.com/google/brotli/commit/67d78bc41db1a0d03f2e763497748f2f69946627
- https://github.com/scrapy/scrapy/commit/14737e91edc513967f516fc839cc9c8a4f8d91da
- https://github.com/google/brotli
- https://github.com/google/brotli/releases/tag/v1.2.0
- https://huntr.com/bounties/2c26a886-5984-47ee-a421-0d5fe1344eb0
