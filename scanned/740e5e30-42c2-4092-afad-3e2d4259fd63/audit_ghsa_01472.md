# [H] Cross-Site Scripting in hexo-admin

## Summary
Severity: High
Advisory: GHSA-phph-xpj4-wvcv
CWE: CWE-79
Ecosystem: npm
Published: 2020-09-03
Source: https://github.com/advisories/GHSA-phph-xpj4-wvcv
Type: github-advisory

## Affected
- npm: `hexo-admin` — affected >=0.0.0

## Details
All versions of `hexo-admin` are vulnerable to Cross-Site Scripting (XSS). The package fails to sanitize rendered markdown, allowing attackers to execute arbitrary JavaScript in a victim's browser if they are able to create new posts.


## Recommendation

No fix is currently available. Consider using an alternative package until a fix is made available.

## References
- https://github.com/jaredly/hexo-admin/issues/185
- https://github.com/jaredly/hexo-admin
- https://www.npmjs.com/advisories/1211
