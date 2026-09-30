# [M] Cookie injection was possible when opening a PDF link

## Summary
Severity: Medium
Advisory: CVE-2026-53900
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:N)
Published: 2026-06-16
Source: https://osv.dev/vulnerability/CVE-2026-53900
Type: osv

## Details
Firefox for iOS preserved cookies set on the initial PDF request across cross-origin HTTP redirects in TemporaryDocument, allowing a malicious site to inject arbitrary cookies into requests to an unrelated target domain. This vulnerability was fixed in Firefox for iOS 152.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53900.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53900
- https://www.mozilla.org/security/advisories/mfsa2026-56/
- https://bugzilla.mozilla.org/show_bug.cgi?id=2043204
