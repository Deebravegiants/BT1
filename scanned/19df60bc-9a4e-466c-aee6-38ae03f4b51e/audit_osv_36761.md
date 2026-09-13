# [H] calibre has a Path Traversal Leading to Arbitrary File Write and Potential Code Execution

## Summary
Severity: High
Advisory: CVE-2026-25635
Aliases: GHSA-32vh-whvh-9fxr
CVSS: 8.6 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H)
Published: 2026-02-06
Source: https://osv.dev/vulnerability/CVE-2026-25635
Type: osv

## Details
calibre is an e-book manager. Prior to 9.2.0, Calibre's CHM reader contains a path traversal vulnerability that allows arbitrary file writes anywhere the user has write permissions. On Windows (haven't tested on other OS's), this can lead to Remote Code Execution by writing a payload to the Startup folder, which executes on next login. This vulnerability is fixed in 9.2.0.

## References
- https://0x5t.raptx.org/posts/calibre-chm-rce
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25635.json
- https://github.com/kovidgoyal/calibre/security/advisories/GHSA-32vh-whvh-9fxr
- https://nvd.nist.gov/vuln/detail/CVE-2026-25635
- https://github.com/kovidgoyal/calibre/commit/9739232fcb029ac15dfe52ccd4fdb4a07ebb6ce9
