# [H] Calibre Affected by Arbitrary Code Execution via Server-Side Template Injection in Calibre HTML Export

## Summary
Severity: High
Advisory: CVE-2026-25731
Aliases: GHSA-xrh9-w7qx-3gcc
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-02-06
Source: https://osv.dev/vulnerability/CVE-2026-25731
Type: osv

## Details
calibre is an e-book manager. Prior to 9.2.0, a Server-Side Template Injection (SSTI) vulnerability in Calibre's Templite templating engine allows arbitrary code execution when a user converts an ebook using a malicious custom template file via the --template-html or --template-html-index command-line options. This vulnerability is fixed in 9.2.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25731.json
- https://github.com/kovidgoyal/calibre/security/advisories/GHSA-xrh9-w7qx-3gcc
- https://nvd.nist.gov/vuln/detail/CVE-2026-25731
- https://github.com/kovidgoyal/calibre/commit/f0649b27512e987b95fcab2e1e0a3bcdafc23379
