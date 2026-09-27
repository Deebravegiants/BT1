# [H] squirrelly Code Injection vulnerability

## Summary
Severity: High
Advisory: GHSA-w5pw-gmcw-rfc8
CVE: CVE-2024-40453
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-08-21
Source: https://github.com/advisories/GHSA-w5pw-gmcw-rfc8
Type: github-advisory

## Affected
- npm: `squirrelly` — affected >=9.0.0 <9.1.0

## Details
squirrellyjs squirrelly v9.0.0 was discovered to contain a code injection vulnerability via the component `options.varName`. The issue was fixed in version 9.1.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-40453
- https://github.com/squirrellyjs/squirrelly/pull/262
- https://github.com/squirrellyjs/squirrelly/commit/426f930e5ca1501404cd887071e734ec5feb0bcf
- https://github.com/squirrellyjs/squirrelly
- https://samuzora.com/posts/cve-2024-40453
