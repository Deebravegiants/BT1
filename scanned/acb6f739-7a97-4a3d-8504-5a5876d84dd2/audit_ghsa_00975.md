# [M] HTML Injection in preact

## Summary
Severity: Medium
Advisory: GHSA-cg48-9hh2-x6mx
CWE: CWE-74
Ecosystem: npm
Published: 2020-09-02
Source: https://github.com/advisories/GHSA-cg48-9hh2-x6mx
Type: github-advisory

## Affected
- npm: `preact` — affected >=10.0.0-alpha.0 <10.0.0-beta.1

## Details
Versions of `preact` 10.x on prerelease tags alpha and beta prior to 10.0.0-beta.1 are vulnerable to HTML Injection. Due to insufficient input validation the package allows attackers to inject JavaScript objects as virtual-dom nodes, which may lead to Cross-Site Scripting. This requires user input parsed with `JSON.parse()` to be passed directly into JSX without sanitization.


## Recommendation

Upgrade to version 10.0.0-beta.1.

## References
- https://github.com/developit/preact/pull/1528
- https://github.com/developit/preact
- https://github.com/developit/preact/releases/tag/10.0.0-beta.1
- https://medium.com/dailyjs/exploiting-script-injection-flaws-in-reactjs-883fb1fe36c1
- https://www.npmjs.com/advisories/835
