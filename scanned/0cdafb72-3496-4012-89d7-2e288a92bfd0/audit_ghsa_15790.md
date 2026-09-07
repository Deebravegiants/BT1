# [H] jrburke requirejs vulnerable to prototype pollution

## Summary
Severity: High
Advisory: GHSA-x3m3-4wpv-5vgc
CVE: CVE-2024-38999
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2024-07-01
Source: https://github.com/advisories/GHSA-x3m3-4wpv-5vgc
Type: github-advisory

## Affected
- npm: `requirejs` — affected >=0 <2.3.7

## Details
jrburke requirejs v2.3.6 was discovered to contain a prototype pollution via the function `s.contexts._.configure`. This vulnerability allows attackers to execute arbitrary code or cause a Denial of Service (DoS) via injecting arbitrary properties.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-38999
- https://github.com/requirejs/r.js/issues/1015
- https://github.com/requirejs/requirejs/issues/1854
- https://github.com/requirejs/requirejs/pull/1856/commits/ebd7a2ff71473542fa132d0d15c10fb4ed1539e1
- https://gist.github.com/mestrtee/9acae342285bd2998fa09ebcb1e6d30a
- https://github.com/requirejs/r.js
- https://security.snyk.io/vuln/SNYK-JS-REQUIREJS-5416713
