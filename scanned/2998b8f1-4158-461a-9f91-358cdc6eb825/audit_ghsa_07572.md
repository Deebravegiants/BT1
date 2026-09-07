# [M] Pannellum has a XSS vulnerability in hot spot attributes

## Summary
Severity: Medium
Advisory: GHSA-8423-w5wx-h2r6
CVE: CVE-2026-27210
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:N/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2026-02-19
Source: https://github.com/advisories/GHSA-8423-w5wx-h2r6
Type: github-advisory

## Affected
- npm: `pannellum` — affected >=2.5.0 <2.5.7

## Details
### Impact
The hot spot `attributes` configuration property allowed any attribute to be set, including HTML event handler attributes, allowing for potential XSS attacks. This affects websites hosting the standalone viewer HTML file and any other use of untrusted JSON config files (bypassing the protections of the `escapeHTML` parameter). As certain events fire without any additional user interaction, visiting a standalone viewer URL that points to a malicious config file&mdash;without additional user interaction&mdash;is sufficient to trigger the vulnerability and execute arbitrary JavaScript code, which can, for example, replace the contents of the page with arbitrary content and make it appear to be hosted by the website hosting the standalone viewer HTML file.

### Patches
This has been fixed both in v2.5.7 and in the current development branch.

### Workarounds
Setting the `Content-Security-Policy` header to `script-src-attr 'none'` will block execution of inline event handlers, mitigating this vulnerability. Don't host `pannellum.htm` on a domain that shares cookies with user authentication to mitigate XSS risk.

### Acknowledgments

Reported both by luminary (@lumin9ry), Visvge (@Sicclord1 / @Visvge), and sutol (@0x5a6163 / @SUT0L) and by another researcher who wishes not to be named at this time.

## References
- https://github.com/mpetroff/pannellum/security/advisories/GHSA-8423-w5wx-h2r6
- https://nvd.nist.gov/vuln/detail/CVE-2026-27210
- https://github.com/mpetroff/pannellum/commit/9391ef8da6a6a98c6a9f8c97f101adb900523681
- https://github.com/mpetroff/pannellum
