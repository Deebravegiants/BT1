# [H] eZ Publish Legacy Passwordless login for LDAP users

## Summary
Severity: High
Advisory: GHSA-p9mp-vq4v-v5m5
CWE: CWE-285
Ecosystem: Packagist
Published: 2024-05-15
Source: https://github.com/advisories/GHSA-p9mp-vq4v-v5m5
Type: github-advisory

## Affected
- Packagist: `ezsystems/ezpublish-legacy` — affected >=2018.9.0 <2018.9.1.1
- Packagist: `ezsystems/ezpublish-legacy` — affected >=2018.6.0 <2018.6.1.2
- Packagist: `ezsystems/ezpublish-legacy` — affected >=2011.0.0 <2017.12.4.1
- Packagist: `ezsystems/ezpublish-legacy` — affected >=5.4.0 <5.4.12.1
- Packagist: `ezsystems/ezpublish-legacy` — affected >=5.3.0 <5.3.12.4

## Details
This security advisory fixes a vulnerability in eZ Publish Legacy, and we recommend that you install it as soon as possible if you are using Legacy.

Installations that are using the legacy LDAP login handler or the TextFile login handler in combination with the standard legacy login handler, may in rare cases be vulnerable to a failure of the standard login handler to verify passwords correctly, allowing unauthorised access.

If your installation has never used the LDAP or TextFile login handlers, or never used legacy login at all, then it is not affected. Still, we recommend installing the update, to be on the safe side.

To install, use Composer to update to one of the "Resolving versions" mentioned above, or apply this patch manually:
https://github.com/ezsystems/ezpublish-legacy/commit/13f03a2be6c0ee4d0caaafaef05904ea9b0c4d9d

## References
- https://github.com/ezsystems/ezpublish-legacy/pull/1394
- https://github.com/ezsystems/ezpublish-legacy/commit/01930a95637389301f762be1439f726013e58aba
- https://github.com/FriendsOfPHP/security-advisories/blob/master/ezsystems/ezpublish-legacy/2018-10-31-1.yaml
- https://github.com/ezsystems/ezpublish-legacy
- https://issues.ibexa.co/browse/EZP-29703
- https://web.archive.org/web/20201027063527/https://magento.com/security/news/new-zend-framework-1-security-vulnerability
- https://web.archive.org/web/20210614184552/https://share.ez.no/community-project/security-advisories/ezsa-2018-005-passwordless-login-for-ldap-users
