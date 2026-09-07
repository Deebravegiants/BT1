# [H] Cross-Site Scripting in wangeditor

## Summary
Severity: High
Advisory: GHSA-g7mw-5cq6-fv82
CWE: CWE-79
Ecosystem: npm
Published: 2020-09-02
Source: https://github.com/advisories/GHSA-g7mw-5cq6-fv82
Type: github-advisory

## Affected
- npm: `wangeditor` — affected >=0

## Details
All versions of `wangeditor` are vulnerable to Cross-Site Scripting. The package fails to properly encode output, allowing arbitrary JavaScript to be inserted in links and executed by browsers.


## Recommendation

No fix is currently available. Consider using an alternative module until a fix is made available.

## References
- https://github.com/wangfupeng1988/wangEditor/issues/1945
- https://github.com/wangfupeng1988/wangEditor
- https://snyk.io/vuln/SNYK-JS-WANGEDITOR-174536
- https://www.npmjs.com/advisories/876
