# [H] Cross-Site Scripting in ids-enterprise

## Summary
Severity: High
Advisory: GHSA-hpfq-8wx8-cgqw
CWE: CWE-79
Ecosystem: npm
Published: 2019-06-13
Source: https://github.com/advisories/GHSA-hpfq-8wx8-cgqw
Type: github-advisory

## Affected
- npm: `ids-enterprise` — affected >=0 <4.18.2

## Details
Versions of `ids-enterprise` prior to 4.18.2 are vulnerable to Cross-Site Scripting (XSS). The `modal` component fails to sanitize input to the `title` attribute, which may allow attackers to execute arbitrary JavaScript.


## Recommendation

Upgrade to version 4.18.2 or later

## References
- https://github.com/infor-design/enterprise-ng/issues/511
- https://github.com/infor-design/enterprise/commit/9b57aaa0321bf2e5baa6c4c5c1eb3b8312e215c4
- https://www.npmjs.com/advisories/957
