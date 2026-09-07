# [C] Magento Patch SUPEE-9652 - Remote Code Execution using mail vulnerability

## Summary
Severity: Critical
Advisory: GHSA-26hq-7286-mg8f
Ecosystem: Packagist
Published: 2024-05-15
Source: https://github.com/advisories/GHSA-26hq-7286-mg8f
Type: github-advisory

## Affected
- Packagist: `magento/community-edition` — affected >=1.9.0.0 <1.14.3.2

## Details
Zend Framework 1 vulnerability can be remotely exploited to execute code in Magento 1. While the issue is not reproducible in Magento 2, the library code is the same so it was fixed as well.

Note: while the vulnerability is scored as critical, few systems are affected. To be affected by the vulnerability the installation has to:

- use sendmail as the mail transport agent

- have specific, non-default configuration settings as described [here](https://magento.com/security/patches/supee-9652#:~:text=settings%20as%20described-,here,-.).

## References
- https://github.com/FriendsOfPHP/security-advisories/blob/master/magento/magento1ee/2017-02-07.yaml
- https://github.com/magento/magento2
- https://web.archive.org/web/20210616204105/https://magento.com/security/patches/supee-9652
