# [M] ZendFramework potential remote code execution in zend-mail via Sendmail adapter

## Summary
Severity: Medium
Advisory: GHSA-gff2-p6vm-3p8g
CWE: CWE-74
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2024-06-07
Source: https://github.com/advisories/GHSA-gff2-p6vm-3p8g
Type: github-advisory

## Affected
- Packagist: `zendframework/zendframework` — affected >=2.0.0 <2.4.11

## Details
When using the zend-mail component to send email via the `Zend\Mail\Transport\Sendmail transport`, a malicious user may be able to inject arbitrary parameters to the system sendmail program. The attack is performed by providing additional quote characters within an address; when unsanitized, they can be interpreted as additional command line arguments, leading to the vulnerability.

## References
- https://github.com/zendframework/zendframework/commit/7c1e89815f5a9c016f4b8088e59b07cb2bf99dc0
- https://github.com/FriendsOfPHP/security-advisories/blob/master/zendframework/zendframework/ZF2016-04.yaml
- https://github.com/zendframework/zendframework
- https://web.archive.org/web/20201107093523/https://framework.zend.com/security/advisory/ZF2016-04
