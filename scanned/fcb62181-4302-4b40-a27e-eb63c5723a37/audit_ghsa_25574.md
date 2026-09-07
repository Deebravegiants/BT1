# [M] SVG with embedded scripts can lead to cross-site scripting attacks in xml2rfc

## Summary
Severity: Medium
Advisory: GHSA-cf4q-4cqr-7g7w
CWE: CWE-79
Ecosystem: PyPI
Published: 2022-04-22
Source: https://github.com/advisories/GHSA-cf4q-4cqr-7g7w
Type: github-advisory

## Affected
- PyPI: `xml2rfc` — affected >=0 <3.12.4

## Details
xml2rfc allows `script` elements in SVG sources.
In HTML output having these script elements can lead to XSS attacks.

Sample XML snippet:
```
<artwork type="svg" src="data:image/svg+xml,%3Csvg viewBox='0 0 10 10' xmlns='http://www.w3.org/2000/svg'%3E%3Cscript%3E window.alert('Test Alert'); %3C/script%3E%3C/svg%3E">
</artwork>
```

### Impact
This vulnerability impacts website that publish HTML drafts and RFCs.

### Patches
This has been fixed in version [3.12.4](https://github.com/ietf-tools/xml2rfc/releases/tag/v3.12.4).

### Workarounds
If SVG source is self-contained within the XML, scraping `script` elements from SVG files.

### References
* https://developer.mozilla.org/en-US/docs/Web/SVG/Element/script

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [xml2rfc](https://github.com/ietf-tools/xml2rfc/)
* Email us at [operational-vulnerability@ietf.org](mailto:operational-vulnerability@ietf.org)
* [Infrastructure and Services Vulnerability Disclosure](https://www.ietf.org/about/administration/policies-procedures/vulnerability-disclosure/)

## References
- https://github.com/ietf-tools/xml2rfc/security/advisories/GHSA-cf4q-4cqr-7g7w
- https://github.com/ietf-tools/xml2rfc
