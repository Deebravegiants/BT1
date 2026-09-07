# [M] Zend_Filter_StripTags vulnerable to Cross-site Scripting when comments allowed

## Summary
Severity: Medium
Advisory: GHSA-4vf6-mq7w-3hp6
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-06-07
Source: https://github.com/advisories/GHSA-4vf6-mq7w-3hp6
Type: github-advisory

## Affected
- Packagist: `zendframework/zendframework1` — affected >=1.7.0 <1.7.9
- Packagist: `zendframework/zendframework1` — affected >=1.8.0 <1.8.5
- Packagist: `zendframework/zendframework1` — affected >=1.9.0 <1.9.7

## Details
Zend_Filter_StripTags contained an optional setting to allow whitelisting HTML comments in filtered text. Microsoft Internet Explorer and several other browsers allow developers to create conditional functionality via HTML comments, including execution of script events and rendering of additional commented markup. By allowing whitelisting of HTML comments, a malicious user could potentially include XSS exploits within HTML comments that would then be rendered in the final output.

## References
- https://github.com/FriendsOfPHP/security-advisories/blob/master/zendframework/zendframework1/ZF2010-03.yaml
- https://github.com/zendframework/zf1
- https://web.archive.org/web/20210411020019/https://framework.zend.com/security/advisory/ZF2010-03
