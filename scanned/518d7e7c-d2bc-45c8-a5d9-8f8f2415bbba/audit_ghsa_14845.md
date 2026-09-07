# [H] Zend-Navigation vulnerable to Cross-site Scripting

## Summary
Severity: High
Advisory: GHSA-6v7p-5qcq-268c
CWE: CWE-352
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2024-06-07
Source: https://github.com/advisories/GHSA-6v7p-5qcq-268c
Type: github-advisory

## Affected
- Packagist: `zendframework/zend-navigation` — affected >=2.0.0 <2.2.7
- Packagist: `zendframework/zend-navigation` — affected >=2.3.0 <2.3.1

## Details
Many Zend Framework 2 view helpers were using the `escapeHtml()` view helper in order to escape HTML attributes, instead of the more appropriate `escapeHtmlAttr()`. In situations where user data and/or JavaScript is used to seed attributes, this can lead to potential cross site scripting (XSS) attack vectors.

Vulnerable view helpers include:

- All `Zend\Form` view helpers.
- Most `Zend\Navigation` (aka `Zend\View\Helper\Navigation\*`) view helpers.
- All "HTML Element" view helpers: `htmlFlash()`, `htmlPage()`, `htmlQuickTime()`.
- `Zend\View\Helper\Gravatar`

## References
- https://framework.zend.com/security/advisory/ZF2014-03
- https://github.com/FriendsOfPHP/security-advisories/blob/master/zendframework/zend-navigation/ZF2014-03.yaml
- https://github.com/zendframework/zend-navigation
