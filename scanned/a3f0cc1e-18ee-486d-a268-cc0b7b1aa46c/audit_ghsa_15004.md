# [M] ZendFramework potential Cross-site Scripting vectors due to inconsistent encodings

## Summary
Severity: Medium
Advisory: GHSA-hg35-vqp3-fv39
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-06-07
Source: https://github.com/advisories/GHSA-hg35-vqp3-fv39
Type: github-advisory

## Affected
- Packagist: `zendframework/zendframework1` — affected >=1.9.0 <1.9.7

## Details
A number of classes, primarily within the `Zend_Form`, `Zend_Filter`, `Zend_Form`, `Zend_Log` and `Zend_View components`, contained character encoding inconsistencies whereby calls to the `htmlspecialchars()` and htmlentities() functions used undefined or hard coded charset parameters. In many of these cases developers were unable to set a character encoding of their choice. These inconsistencies could, in specific circumstances, allow certain multibyte representations of special HTML characters pass through unescaped leaving applications potentially vulnerable to cross-site scripting (XSS) exploits. Such exploits would only be possible if a developer used a non-typical character encoding (such as UTF-7), allowed users to define the character encoding, or served HTML documents without a valid character set defined.

## References
- https://framework.zend.com/security/advisory/ZF2010-01
- https://github.com/FriendsOfPHP/security-advisories/blob/master/zendframework/zendframework1/ZF2010-01.yaml
- https://github.com/zendframework/zf1
