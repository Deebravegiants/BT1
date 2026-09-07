# [M] Wallabag cross-site scripting (XSS) vulnerability

## Summary
Severity: Medium
Advisory: GHSA-gvcw-x64m-pfcj
CVE: CVE-2018-11352
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:H/PR:H/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-gvcw-x64m-pfcj
Type: github-advisory

## Affected
- Packagist: `wallabag/wallabag` — affected >=2.2.3 <2.3.3

## Details
The Wallabag application 2.2.3 to 2.3.2 is affected by one cross-site scripting (XSS) vulnerability that is stored within the configuration page. This vulnerability enables the execution of a JavaScript payload each time an administrator visits the configuration page. The vulnerability can be exploited with authentication and used to target administrators and steal their sessions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-11352
- https://bishopfox.com/blog/wallabag-2-2-3-to-2-3-2-stored-cross-site-scripting
- https://github.com/wallabag/wallabag
