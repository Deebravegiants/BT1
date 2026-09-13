# [C] DBAL 3 SQL Injection Security Vulnerability

## Summary
Severity: Critical
Advisory: GHSA-r7cj-8hjg-x622
CVE: CVE-2021-43608
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-11-16
Source: https://github.com/advisories/GHSA-r7cj-8hjg-x622
Type: github-advisory

## Affected
- Packagist: `doctrine/dbal` — affected >=3.0.0 <3.1.4

## Details
We have released a new version Doctrine DBAL 3.1.4 that fixes a critical SQL injection vulnerability in the LIMIT clause generation API provided by the Platform abstraction.

We advise everyone using Doctrine DBAL 3.0.0 up to 3.1.3 to upgrade to 3.1.4 immediately.

The vulnerability can happen when unsanitized input is passed to many APIs in Doctrine DBAL and ORM that ultimately end up calling `AbstractPlatform::modifyLimitQuery`. 

As a workaround you can cast all limit and offset parameters to integers before passing them to Doctrine APIs.

This vulnerability has been assigned [CVE-2021-43608](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2021-43608).

## References
- https://github.com/doctrine/dbal/security/advisories/GHSA-r7cj-8hjg-x622
- https://nvd.nist.gov/vuln/detail/CVE-2021-43608
- https://github.com/doctrine/dbal/commit/9dcfa4cb6c03250b78a84737ba7ceb82f4b7ba4d
- https://github.com/FriendsOfPHP/security-advisories/blob/master/doctrine/dbal/CVE-2021-43608.yaml
- https://github.com/doctrine/dbal
- https://github.com/doctrine/dbal/releases
- https://www.doctrine-project.org/2021/11/11/dbal3-vulnerability-fixed.html
