# [H] Doctrine DBAL SQL injection possibility

## Summary
Severity: High
Advisory: GHSA-76w8-mqx4-wjrf
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:L/A:L (CVSS_V3)
Published: 2024-05-15
Source: https://github.com/advisories/GHSA-76w8-mqx4-wjrf
Type: github-advisory

## Affected
- Packagist: `doctrine/dbal` — affected >=2.0.0 <2.0.8
- Packagist: `doctrine/dbal` — affected >=2.1.0 <2.1.2

## Details
The identifier quoting in Doctrine DBAL has a potential security problem when user-input is passed into this function, making the security aspect of this functionality obsolete.
If you make use of AbstractPlatform::quoteIdentifier() or Doctrine::quoteIdentifier() please upgrade immediately. The ORM itself does not use identifier quoting in combination with user-input, however we still urge everyone to update to the latest version of DBAL.

## References
- https://github.com/FriendsOfPHP/security-advisories/blob/master/doctrine/dbal/2011-09-25.yaml
- https://github.com/doctrine/dbal
- https://web.archive.org/web/20130208100252/https://www.doctrine-project.org/blog/dbal-security-2011-1.html
