# [M] Zend-Form vulnerable to Cross-site Scripting

## Summary
Severity: Medium
Advisory: GHSA-gvpp-6jrj-5pqc
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-06-07
Source: https://github.com/advisories/GHSA-gvpp-6jrj-5pqc
Type: github-advisory

## Affected
- Packagist: `zendframework/zend-form` — affected >=2.0.0 <2.2.7
- Packagist: `zendframework/zend-form` — affected >=2.3.0 <2.3.1

## Details
Many Zend Framework 2 view helpers were using the escapeHtml() view helper in order to escape HTML attributes, instead of the more appropriate escapeHtmlAttr(). In situations where user data and/or JavaScript is used to seed attributes, this can lead to potential cross site scripting (XSS) attack vectors.

Vulnerable view helpers include:

- All `Zend\Form` view helpers.
- Most `Zend\Navigation` (aka `Zend\View\Helper\Navigation\*`) view helpers.
- All "HTML Element" view helpers: `htmlFlash()`, `htmlPage()`, `htmlQuickTime()`.
- `Zend\View\Helper\Gravatar`

## References
- https://github.com/zendframework/zend-form/commit/6fe40314e8e3477494aadd03d62573bd1c212bd1
- https://github.com/zendframework/zend-form/commit/d7a1f5bc4626b1df990391502a868b28c37ba65d
- https://github.com/zendframework/zend-form/commit/fd43a951460c4bc60c77a566129705f6bdb9c61b
- https://framework.zend.com/security/advisory/ZF2014-03
- https://github.com/FriendsOfPHP/security-advisories/blob/master/zendframework/zend-form/ZF2014-03.yaml
- https://github.com/zendframework/zend-form
