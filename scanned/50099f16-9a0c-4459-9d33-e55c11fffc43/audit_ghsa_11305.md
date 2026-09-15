# [H] path-to-regexp vulnerable to Denial of Service via sequential optional groups

## Summary
Severity: High
Advisory: GHSA-j3q9-mxjg-w52f
CVE: CVE-2026-4926
CWE: CWE-1333, CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-03-27
Source: https://github.com/advisories/GHSA-j3q9-mxjg-w52f
Type: github-advisory

## Affected
- npm: `path-to-regexp` — affected >=8.0.0 <8.4.0

## Details
### Impact

A bad regular expression is generated any time you have multiple sequential optional groups (curly brace syntax), such as `{a}{b}{c}:z`. The generated regex grows exponentially with the number of groups, causing denial of service.

### Patches

Fixed in version 8.4.0.

### Workarounds

Limit the number of sequential optional groups in route patterns. Avoid passing user-controlled input as route patterns.

## References
- https://github.com/pillarjs/path-to-regexp/security/advisories/GHSA-j3q9-mxjg-w52f
- https://nvd.nist.gov/vuln/detail/CVE-2026-4926
- https://cna.openjsf.org/security-advisories.html
- https://github.com/pillarjs/path-to-regexp
