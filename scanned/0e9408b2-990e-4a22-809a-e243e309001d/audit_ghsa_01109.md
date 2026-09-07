# [H] Cross-Site Scripting in bleach

## Summary
Severity: High
Advisory: GHSA-5634-rv46-48jf
CWE: CWE-79
Ecosystem: npm
Published: 2020-09-03
Source: https://github.com/advisories/GHSA-5634-rv46-48jf
Type: github-advisory

## Affected
- npm: `bleach` — affected >=0.0.0

## Details
All versions of `bleach` are vulnerable to Cross-Site Scripting. It is possible to bypass the package's HTML sanitization with payloads such as `"<<script><</script>script>alert('xss');</<script><</script>script>"` regardless of the passed options. This may allow attackers to execute arbitrary JavaScript in the victim's browser.


## Recommendation

No fix is currently available. Consider using an alternative package until a fix is made available.

## References
- https://www.npmjs.com/advisories/1034
