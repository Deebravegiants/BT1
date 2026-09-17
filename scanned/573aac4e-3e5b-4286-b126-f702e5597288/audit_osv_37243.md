# [M] Business Logic Error on OpenProject through hyperlinks in markdown using DOM clobbering

## Summary
Severity: Medium
Advisory: CVE-2026-30235
Aliases: GHSA-9rv2-9xv5-gpq8
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-03-11
Source: https://osv.dev/vulnerability/CVE-2026-30235
Type: osv

## Details
OpenProject is an open-source, web-based project management software. Prior to 17.2.0, this vulnerability occurs due to improper validation of OpenProject’s Markdown rendering, specifically in the hyperlink handling. This allows an attacker to inject malicious hyperlink payloads that perform DOM clobbering. DOM clobbering can crash or blank the entire page by overwriting native DOM functions with HTML elements, causing critical JavaScript calls to throw runtime errors during application initialization and halt further execution. This vulnerability is fixed in 17.2.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/30xxx/CVE-2026-30235.json
- https://github.com/opf/openproject/security/advisories/GHSA-9rv2-9xv5-gpq8
- https://nvd.nist.gov/vuln/detail/CVE-2026-30235
