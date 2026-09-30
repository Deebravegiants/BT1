# [H] WeasyPrint allows the attachment of arbitrary files and URLs to a PDF

## Summary
Severity: High
Advisory: GHSA-35jj-wx47-4w8r
CVE: CVE-2024-28184
CWE: CWE-829
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:L (CVSS_V3)
Published: 2024-03-08
Source: https://github.com/advisories/GHSA-35jj-wx47-4w8r
Type: github-advisory

## Affected
- PyPI: `weasyprint` — affected >=61.0 <61.2

## Details
### Impact
Since version 61.0, there's a vulnerability which allows attaching content of arbitrary files and URLs to a generated PDF document, even if `url_fetcher` is configured to prevent access to files and URLs.

### Patches
Fixed by 734ee8e that’s included in 61.2

### Workarounds
- Check that no PDF attachment is defined in source HTML.
- Launch WeasyPrint in a sandbox that prevents access to the filesystem and the network.

## References
- https://github.com/Kozea/WeasyPrint/security/advisories/GHSA-35jj-wx47-4w8r
- https://nvd.nist.gov/vuln/detail/CVE-2024-28184
- https://github.com/Kozea/WeasyPrint/commit/734ee8e2dc84ff3090682f3abff056d0907c8598
- https://github.com/Kozea/WeasyPrint
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/ZLQZMOEDY72TS43HDXOBVID2VYCTWIH6
