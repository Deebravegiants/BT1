# [H] Zend Framework CSRF Vulnerability

## Summary
Severity: High
Advisory: GHSA-gwwq-54qp-9pgp
CVE: CVE-2015-1786
CWE: CWE-352
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-gwwq-54qp-9pgp
Type: github-advisory

## Affected
- Packagist: `zendframework/zendframework` — affected >=2.3.0 <2.3.6

## Details
Cross-site request forgery (CSRF) vulnerability in Zend/Validator/Csrf in Zend Framework 2.3.x before 2.3.6 via null or malformed token identifiers.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-1786
- https://github.com/zendframework/zendframework/commit/213d2c490f55331ba4e5e3884bd81d13d1eb0aee
- https://bugzilla.redhat.com/show_bug.cgi?id=1207781
- https://framework.zend.com/changelog/2.3.6
- https://framework.zend.com/security/advisory/ZF2015-03
- https://github.com/FriendsOfPHP/security-advisories/blob/master/zendframework/zendframework/CVE-2015-1786.yaml
- https://github.com/zendframework/zf-web/blob/f97fe5c3cf6c51df7502237c6342511802c8df22/module/Security/view/security/advisory/ZF2015-03.phtml
- https://github.com/zendframework/zf3-web/blob/5852ab5bfd47285e6b46f9e7b13250629b3e372e/data/advisories/ZF2015-03.md
