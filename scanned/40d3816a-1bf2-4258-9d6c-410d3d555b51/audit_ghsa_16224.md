# [H] Scrapy vulnerable to ReDoS via XMLFeedSpider

## Summary
Severity: High
Advisory: GHSA-cc65-xxvf-f7r9
CVE: CVE-2024-1892
CWE: CWE-1333
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-02-15
Source: https://github.com/advisories/GHSA-cc65-xxvf-f7r9
Type: github-advisory

## Affected
- PyPI: `scrapy` — affected >=2 <2.11.1
- PyPI: `scrapy` — affected >=0 <1.8.4

## Details
### Impact

The following parts of the Scrapy API were found to be vulnerable to a [ReDoS attack](https://owasp.org/www-community/attacks/Regular_expression_Denial_of_Service_-_ReDoS):

- The [`XMLFeedSpider`](https://docs.scrapy.org/en/latest/topics/spiders.html#scrapy.spiders.XMLFeedSpider) class or any subclass that uses the default node iterator: `iternodes`, as well as direct uses of the `scrapy.utils.iterators.xmliter` function.

- **Scrapy 2.6.0 to 2.11.0**: The [`open_in_browser`](https://docs.scrapy.org/en/latest/topics/debug.html#scrapy.utils.response.open_in_browser) function for a response without a [base tag](https://www.w3schools.com/tags/tag_base.asp). 

Handling a malicious response could cause extreme CPU and memory usage during the parsing of its content, due to the use of vulnerable regular expressions for that parsing.

### Patches

Upgrade to Scrapy 2.11.1.

If you are using Scrapy 1.8 or a lower version, and upgrading to Scrapy 2.11.1 is not an option, you may upgrade to Scrapy 1.8.4 instead.

### Workarounds

For `XMLFeedSpider`, switch the node iterator to ``xml`` or ``html``.

For `open_in_browser`, before using the function, either manually review the response content to discard a ReDos attack or manually define the base tag to avoid its automatic definition by `open_in_browser` later.

### Acknowledgements

This security issue was reported by @nicecatch2000  [through huntr.com](https://huntr.com/bounties/271f94f2-1e05-4616-ac43-41752389e26b/).

## References
- https://github.com/scrapy/scrapy/security/advisories/GHSA-cc65-xxvf-f7r9
- https://github.com/scrapy/scrapy/commit/479619b340f197a8f24c5db45bc068fb8755f2c5
- https://github.com/scrapy/scrapy/commit/73e7c0ed011a0565a1584b8052ec757b54e5270b
- https://docs.scrapy.org/en/latest/news.html#scrapy-1-8-4-2024-02-14
- https://docs.scrapy.org/en/latest/news.html#scrapy-2-11-1-2024-02-14
- https://github.com/pypa/advisory-database/tree/main/vulns/scrapy/PYSEC-2024-162.yaml
- https://github.com/scrapy/scrapy
- https://huntr.com/bounties/271f94f2-1e05-4616-ac43-41752389e26b
