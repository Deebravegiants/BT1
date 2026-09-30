# [M] Local File Inclusion in domokeeper

## Summary
Severity: Medium
Advisory: GHSA-cr67-78jr-j94p
Ecosystem: npm
Published: 2020-09-03
Source: https://github.com/advisories/GHSA-cr67-78jr-j94p
Type: github-advisory

## Affected
- npm: `domokeeper` — affected >=0.0.0

## Details
All versions of `domokeeper` are vulnerable to Local File Inclusion. The `/plugin/` route passes a GET parameter unsanitized to a `require()` call. It then returns the output of `require()` in the server response. This may allow attackers to load unintended code in the application. It also allows attackers to exfiltrate information in `.json` files.


## Recommendation

No fix is currently available. Consider using an alternative package until a fix is made available.

## References
- https://www.npmjs.com/advisories/1075
