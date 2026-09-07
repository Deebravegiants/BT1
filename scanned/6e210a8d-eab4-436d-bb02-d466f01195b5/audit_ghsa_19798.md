# [M] JS Html Sanitizer allows XSS when used with contentEditable

## Summary
Severity: Medium
Advisory: GHSA-vhv4-fh94-jm5x
CVE: CVE-2025-29771
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2025-03-14
Source: https://github.com/advisories/GHSA-vhv4-fh94-jm5x
Type: github-advisory

## Affected
- npm: `@jitbit/htmlsanitizer` — affected >=0 <2.0.3

## Details
### Impact
XSS vulnerability when the sanitizer is used with a `contentEditable` element to set the elements `innerHTML` to a sanitized string produced by the package. If the code is particularly crafted to abuse the code beautifier, that runs AFTER sanitation.

### Patches
Patched in version 2.0.3

## References
- https://github.com/jitbit/HtmlSanitizer/security/advisories/GHSA-vhv4-fh94-jm5x
- https://nvd.nist.gov/vuln/detail/CVE-2025-29771
- https://github.com/jitbit/HtmlSanitizer/commit/af6d2a78877e7277cd01c825b7fb50edb5956963
- https://github.com/jitbit/HtmlSanitizer
