# [H] Cross-Site Scripting in mermaid

## Summary
Severity: High
Advisory: GHSA-w32g-5hqp-gg6q
CWE: CWE-79
Ecosystem: npm
Published: 2020-09-02
Source: https://github.com/advisories/GHSA-w32g-5hqp-gg6q
Type: github-advisory

## Affected
- npm: `mermaid` — affected >=0 <8.2.3

## Details
Versions of `mermaid` prior to 8.2.3 are vulnerable to Cross-Site Scripting. If malicious input  such as `A["<img src=invalid onerror=alert('XSS')></img>"] ` is provided to the application, it will execute the code instead of rendering it as text due to improper output encoding.


## Recommendation

Upgrade to version 8.2.3 or later

## References
- https://github.com/knsv/mermaid/issues/847
- https://github.com/knsv/mermaid
- https://www.npmjs.com/advisories/751
