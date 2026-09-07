# [H] Angular critical CSS inlining Cross-site Scripting Vulnerability Advisory

## Summary
Severity: High
Advisory: GHSA-r3hf-q8q7-fv2p
CWE: CWE-79
Ecosystem: npm
Published: 2023-08-09
Source: https://github.com/advisories/GHSA-r3hf-q8q7-fv2p
Type: github-advisory

## Affected
- npm: `@nguniversal/common` — affected >=16.1.0 <16.1.2

## Details
### Impact
Angular Universal applications on 16.1.0 and 16.1.1 using critical CSS inlining are vulnerable to a [cross-site scripting (XSS)](https://owasp.org/www-community/attacks/xss/) attack where an attacker can trick another user into visiting a page which injects malicious JavaScript.

Angular CLI applications without Universal do perform critical CSS inlining as well, however exploiting this requires a malicious actor to already have access to modify source code directly.

### Patches
`@nguniversal/common` should be upgraded to 16.1.2 or higher. 16.2.0-rc.0 is safe.

### Workarounds
The easiest solution is likely to upgrade Universal to 16.1.2 or downgrade to 16.0.x or lower. Alternatively you can [override](https://docs.npmjs.com/cli/v9/configuring-npm/package-json#overrides) specifically the `critters` dependency with version `0.0.20` in your `package.json`.

```json
{
  "overrides": {
    "critters": "0.0.20"
  }
}
```

### References

* [Angular Blog Post](https://blog.angular.io/notice-of-xss-issue-affecting-angular-universal-16-1-0-16-1-1-95dbae068f)

## References
- https://github.com/angular/universal/security/advisories/GHSA-r3hf-q8q7-fv2p
- https://github.com/angular/universal
