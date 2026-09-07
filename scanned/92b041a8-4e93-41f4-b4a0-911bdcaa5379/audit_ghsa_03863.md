# [M] Composer JavaScript injection possible via html comments

## Summary
Severity: Medium
Advisory: GHSA-fm68-89m8-4gjj
CVE: CVE-2019-8233
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2019-11-12
Source: https://github.com/advisories/GHSA-fm68-89m8-4gjj
Type: github-advisory

## Affected
- Packagist: `magento/community-edition` — affected >=2.2 <2.2.10
- Packagist: `magento/community-edition` — affected >=2.3 <2.3.3

## Details
In Magento 2.2 prior to 2.2.10, Magento 2.3 prior to 2.3.3 or 2.3.2-p1, an unauthenticated user can inject arbitrary JavaScript code as a result of the sanitization engine ignoring HTML comments.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-8233
- https://github.com/magento/magento2
- https://magento.com/security/patches/magento-2.3.3-and-2.2.10-security-update
