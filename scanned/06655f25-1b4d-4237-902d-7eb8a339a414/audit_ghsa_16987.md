# [H] Contao: Possible cookie sharing with external domains while checking protected pages for broken links

## Summary
Severity: High
Advisory: GHSA-9jh5-qf84-x6pr
CVE: CVE-2024-28235
CWE: CWE-200
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2024-04-09
Source: https://github.com/advisories/GHSA-9jh5-qf84-x6pr
Type: github-advisory

## Affected
- Packagist: `contao/core-bundle` — affected >=4.9.0 <4.13.40
- Packagist: `contao/core-bundle` — affected >=5.0.0-RC1 <5.3.4

## Details
### Impact

If the crawler is set to crawl protected pages, it sends the cookie header to externals URLs.

### Patches

Update to Contao 4.13.40 or 5.3.4.

### Workarounds

Disable crawling protected pages.

### References

https://contao.org/en/security-advisories/session-cookie-disclosure-in-the-crawler

### For more information

If you have any questions or comments about this advisory, open an issue in [contao/contao](https://github.com/contao/contao/issues/new/choose).

## References
- https://github.com/contao/contao/security/advisories/GHSA-9jh5-qf84-x6pr
- https://nvd.nist.gov/vuln/detail/CVE-2024-28235
- https://github.com/contao/contao/commit/73a2770e2d3535ec9f1b03d54be00e56ebb8ff16
- https://github.com/contao/contao/commit/79b7620d01ce8f46ce2b331455e0d95e5208de3d
- https://contao.org/en/security-advisories/session-cookie-disclosure-in-the-crawler
- https://github.com/contao/contao
- https://github.com/contao/contao/blob/14e9ef4bc8b82936ba2d0e04164581145a075e2a/core-bundle/src/Resources/contao/classes/Crawl.php#L129
