# [H] Cross-Site Scripting in bootstrap-vue

## Summary
Severity: High
Advisory: GHSA-c7pp-x73h-4m2v
CWE: CWE-79
Ecosystem: npm
Published: 2020-09-02
Source: https://github.com/advisories/GHSA-c7pp-x73h-4m2v
Type: github-advisory

## Affected
- npm: `bootstrap-vue` — affected >=0 <2.0.0-rc.12

## Details
Versions of `bootstrap-vue` prior to 2.0.0-rc.12 are vulnerable to Cross-Site Scripting. Due to insufficient input sanitization, components may be vulnerable to Cross-Site Scripting through the `options` variable. This may lead to the execution of malicious JavaScript on the user's browser.


## Recommendation

Upgrade to version 2.0.0-rc.12 or later.

## References
- https://github.com/bootstrap-vue/bootstrap-vue/issues/1974
- https://github.com/bootstrap-vue/bootstrap-vue/pull/2134
- https://github.com/bootstrap-vue/bootstrap-vue/commit/ba6f3f8359e257589d744f180312c09bf9f12289
- https://github.com/bootstrap-vue/bootstrap-vue
- https://www.npmjs.com/advisories/770
