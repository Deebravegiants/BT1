# [H] eZ Platform User data disclosure

## Summary
Severity: High
Advisory: GHSA-3g43-xfrw-pv5m
CWE: CWE-200
Ecosystem: Packagist
Published: 2024-05-15
Source: https://github.com/advisories/GHSA-3g43-xfrw-pv5m
Type: github-advisory

## Affected
- Packagist: `ezsystems/repository-forms` — affected >=2.3.0 <2.3.2.1

## Details
In eZ Platform v2.3.x it is possible to bypass permission checks in a particular case. This means user data such as name and email (but not passwords or password hashes) can be read by unauthenticated users. This affects only v2.3.x. If you use v2.2.x or older you are not affected.

To install, use Composer to update "ezsystems/repository-forms" to the "Resolving versions" mentioned above, or apply this patch manually:
https://github.com/ezsystems/repository-forms/commit/ea82e136ec1ea40aca714abb79cc8e5bfece01e8

Have you found a security bug in eZ Publish or eZ Platform? See how to report it responsibly here: https://doc.ez.no/Security

## References
- https://github.com/ezsystems/repository-forms/commit/ea82e136ec1ea40aca714abb79cc8e5bfece01e8
- https://github.com/FriendsOfPHP/security-advisories/blob/master/ezsystems/repository-forms/2018-11-20-1.yaml
- https://github.com/ezsystems/repository-forms
- https://web.archive.org/web/20210614184249/http://share.ez.no/community-project/security-advisories/ezsa-2018-007-user-data-disclosure
- http://share.ez.no/community-project/security-advisories/ezsa-2018-007-user-data-disclosure
