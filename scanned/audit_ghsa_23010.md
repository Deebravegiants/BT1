# [M] Zenario CMS vulnerable to CRLF injection 

## Summary
Severity: Medium
Advisory: GHSA-5957-5crx-79jx
CVE: CVE-2015-3154
CWE: CWE-74
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-5957-5crx-79jx
Type: github-advisory

## Affected
- Packagist: `zendframework/zend-http` — affected >=2.0.0beta4 <2.3.8
- Packagist: `zendframework/zend-http` — affected >=2.4.0rc1 <2.4.1
- Packagist: `zendframework/zendframework` — affected >=2.0.0beta4 <2.3.8
- Packagist: `zendframework/zendframework` — affected >=2.4.0rc1 <2.4.1
- Packagist: `zendframework/zendframework1` — affected >=0 <1.12.12
- Packagist: `zendframework/zend-http` — affected >=0 <1.12.12

## Details
CRLF injection vulnerability in Zend\Mail (Zend_Mail) in Zend Framework before 1.12.12, 2.x before 2.3.8, and 2.4.x before 2.4.1 allows remote attackers to inject arbitrary HTTP headers and conduct HTTP response splitting attacks via CRLF sequences in the header of an email.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-3154
- https://framework.zend.com/security/advisory/ZF2015-04
- https://github.com/FriendsOfPHP/security-advisories/blob/master/zendframework/zend-http/CVE-2015-3154.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/zendframework/zendframework/CVE-2015-3154.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/zendframework/zendframework1/CVE-2015-3154.yaml
- https://github.com/zendframework/zendframework
