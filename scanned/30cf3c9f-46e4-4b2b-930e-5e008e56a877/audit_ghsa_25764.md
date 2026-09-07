# [M] Cross-site Scripting in Parsedown

## Summary
Severity: Medium
Advisory: GHSA-qgpv-86r3-87fh
CVE: CVE-2018-1000162
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-03-30
Source: https://github.com/advisories/GHSA-qgpv-86r3-87fh
Type: github-advisory

## Affected
- Packagist: `erusev/parsedown` — affected >=0 <1.7.0

## Details
Parsedown version prior to 1.7.0 contains a Cross Site Scripting (XSS) vulnerability in `setMarkupEscaped` for escaping HTML that can result in JavaScript code execution. This attack appears to be exploitable via specially crafted markdown that allows it to side step HTML escaping by breaking AST boundaries. This vulnerability appears to have been fixed in 1.7.0 and later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000162
- https://github.com/Roave/SecurityAdvisories/issues/44#issuecomment-368594409
- https://github.com/erusev/parsedown/pull/495
- https://github.com/FriendsOfPHP/security-advisories/blob/master/erusev/parsedown/CVE-2018-1000162.yaml
- https://github.com/erusev/parsedown
