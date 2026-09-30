# [M] Misinterpretation of malicious XML input

## Summary
Severity: Medium
Advisory: GHSA-5fg8-2547-mr8q
CVE: CVE-2021-32796
CWE: CWE-116
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2021-08-03
Source: https://github.com/advisories/GHSA-5fg8-2547-mr8q
Type: github-advisory

## Affected
- npm: `xmldom` — affected >=0
- npm: `@xmldom/xmldom` — affected >=0 <0.7.0

## Details
### Impact
xmldom versions 0.6.0 and older do not correctly escape special characters when serializing elements removed from their ancestor. This may lead to unexpected syntactic changes during XML processing in some downstream applications.

### Patches
Update to one of the fixed versions of `@xmldom/xmldom` (`>=0.7.0`)

See issue #271 for the status of publishing `xmldom` to npm or join #270 for Q&A/discussion until it's resolved.

### Workarounds

Downstream applications can validate the input and reject the maliciously crafted documents.

### References

Similar to this one reported on the Go standard library:

- https://mattermost.com/blog/coordinated-disclosure-go-xml-vulnerabilities/
- https://mattermost.com/blog/securing-xml-implementations-across-the-web/

### For more information

If you have any questions or comments about this advisory:

* Open an issue in [`xmldom/xmldom`](https://github.com/xmldom/xmldom)
* Email us: send an email to **all** addresses that are shown by `npm owner ls @xmldom/xmldom`

## References
- https://github.com/xmldom/xmldom/security/advisories/GHSA-5fg8-2547-mr8q
- https://nvd.nist.gov/vuln/detail/CVE-2021-32796
- https://github.com/xmldom/xmldom/commit/7b4b743917a892d407356e055b296dcd6d107e8b
- https://github.com/xmldom/xmldom
- https://mattermost.com/blog/coordinated-disclosure-go-xml-vulnerabilities
- https://mattermost.com/blog/securing-xml-implementations-across-the-web
- https://www.npmjs.com/package/@xmldom/xmldom
