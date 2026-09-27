# [H] PYSEC-2024-235

## Summary
Severity: High
Advisory: PYSEC-2024-235
Aliases: CVE-2024-0243, GHSA-h9j7-5xvc-qhg5, PYSEC-2026-1509
Ecosystem: PyPI
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-02-26
Source: https://osv.dev/vulnerability/PYSEC-2024-235
Type: osv

## Affected
- PyPI: `langchain-exa` — affected >=0 <bf0b3cc0b5ade1fb95a5b1b6fa260e99064c2e22, >=0 <0.1.0

## Details
With the following crawler configuration:

```python
from bs4 import BeautifulSoup as Soup

url = "https://example.com"
loader = RecursiveUrlLoader(
    url=url, max_depth=2, extractor=lambda x: Soup(x, "html.parser").text
)
docs = loader.load()
```

An attacker in control of the contents of `https://example.com` could place a malicious HTML file in there with links like "https://example.completely.different/my_file.html" and the crawler would proceed to download that file as well even though `prevent_outside=True`.

https://github.com/langchain-ai/langchain/blob/bf0b3cc0b5ade1fb95a5b1b6fa260e99064c2e22/libs/community/langchain_community/document_loaders/recursive_url_loader.py#L51-L51

Resolved in https://github.com/langchain-ai/langchain/pull/15559

## References
- https://huntr.com/bounties/370904e7-10ac-40a4-a8d4-e2d16e1ca861
- https://github.com/langchain-ai/langchain/commit/bf0b3cc0b5ade1fb95a5b1b6fa260e99064c2e22
- https://github.com/langchain-ai/langchain/pull/15559
