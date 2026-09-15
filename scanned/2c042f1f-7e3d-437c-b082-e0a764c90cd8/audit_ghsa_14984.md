# [H] Zendframework Local file disclosure via XXE injection in Zend_XmlRpc

## Summary
Severity: High
Advisory: GHSA-229x-22xc-2f2w
CWE: CWE-611
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2024-06-07
Source: https://github.com/advisories/GHSA-229x-22xc-2f2w
Type: github-advisory

## Affected
- Packagist: `zendframework/zendframework1` — affected >=1.0.0 <1.11.13

## Details
Zend_XmlRpc is vulnerable to XML eXternal Entity (XXE) Injection attacks. The SimpleXMLElement class (SimpleXML PHP extension) is used in an insecure way to parse XML data. External entities can be specified by adding a specific DOCTYPE element to XML-RPC requests. By exploiting this vulnerability an application may be coerced to open arbitrary files and/or TCP connections.

## References
- https://github.com/FriendsOfPHP/security-advisories/blob/master/zendframework/zendframework1/ZF2012-01.yaml
- https://github.com/zendframework/zf1
- https://web.archive.org/web/20210620092354/https://framework.zend.com/security/advisory/ZF2012-01
