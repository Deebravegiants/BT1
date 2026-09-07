# [M] Cross-Site Scripting in @nuxt/devalue

## Summary
Severity: Medium
Advisory: GHSA-6677-83pp-f862
CVE: CVE-2019-13506
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2019-07-16
Source: https://github.com/advisories/GHSA-6677-83pp-f862
Type: github-advisory

## Affected
- npm: `@nuxt/devalue` — affected >=0 <1.2.3

## Details
Versions of `@nuxt/devalue` prior to 1.2.3 are vulnerable to Cross-Site Scripting. Due to insufficient input sanitization attacker may inject arbitrary JavaScript code through object keys.


## Recommendation

Upgrade to version 1.2.3 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-13506
- https://github.com/Rich-Harris/devalue/issues/19
- https://github.com/nuxt/devalue/pull/8
- https://github.com/nuxt/nuxt.js/commit/0d5dfe71917191c5b07f373896311f2d8f6b75be
- https://github.com/nuxt/devalue/releases/tag/v1.2.3
- https://github.com/nuxt/nuxt.js/compare/c0776eb...8d14cd4
- https://github.com/nuxt/nuxt.js/releases/tag/v2.6.2
- https://www.npmjs.com/advisories/814
