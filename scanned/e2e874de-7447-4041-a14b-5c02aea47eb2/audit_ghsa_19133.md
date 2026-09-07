# [H] DOM Expressions has a Cross-Site Scripting (XSS) vulnerability due to improper use of string.replace

## Summary
Severity: High
Advisory: GHSA-hw62-58pr-7wc5
CVE: CVE-2025-27108
CWE: CWE-116, CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2025-02-25
Source: https://github.com/advisories/GHSA-hw62-58pr-7wc5
Type: github-advisory

## Affected
- npm: `dom-expressions` — affected >=0 <0.39.5

## Details
> [!NOTE]  
> This advisory was originally emailed to community@solidjs.com by @nsysean.

To sum it up, the use of javascript's `.replace()` opens up to potential XSS vulnerabilities with the special replacement patterns beginning with `$`.

Particularly, when the attributes of `Meta` tag from solid-meta are user-defined, attackers can utilise the special replacement patterns, either `$'` or `$\`` to achieve XSS.

The solid-meta package has this issue since it uses `useAffect` and context providers, which injects the used assets in the html header. "dom-expressions" uses `.replace()` to insert the assets, which is vulnerable to the special replacement patterns listed above. 

This effectively means that if the attributes of an asset tag contained user-controlled data, it would be vulnerable to XSS. For instance, there might be meta tags for the open graph protocol in a user profile page, but if attackers set the user query to some payload abusing `.replace()`, then they could execute arbitrary javascript in the victim's web browser. Moreover, it could be stored and cause more problems.

## References
- https://github.com/ryansolid/dom-expressions/security/advisories/GHSA-hw62-58pr-7wc5
- https://nvd.nist.gov/vuln/detail/CVE-2025-27108
- https://github.com/ryansolid/dom-expressions/commit/521f75dfa89ed24161646e7007d9d7d21da07767
- https://github.com/ryansolid/dom-expressions
