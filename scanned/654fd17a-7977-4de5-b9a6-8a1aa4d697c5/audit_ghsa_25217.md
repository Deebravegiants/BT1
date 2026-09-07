# [H] XXE in SabreDAV

## Summary
Severity: High
Advisory: GHSA-qm4x-ch5w-gr62
CVE: CVE-2014-2055
Ecosystem: Packagist
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-qm4x-ch5w-gr62
Type: github-advisory

## Affected
- Packagist: `sabre/dav` — affected >=1.6.0 <1.7.11
- Packagist: `sabre/dav` — affected >=1.8.0 <1.8.9

## Details
SabreDAV before 1.7.11, as used in ownCloud Server before 5.0.15 and 6.0.x before 6.0.2, allows remote attackers to read arbitrary files, cause a denial of service, or possibly have other impact via an XML External Entity (XXE) attack.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-2055
- https://github.com/sabre-io/dav/issues/414
- https://github.com/sabre-io/dav/commit/e3f46e0ecf83cf1d2ebf54908cde7b5ec170aa2c
- https://github.com/FriendsOfPHP/security-advisories/blob/master/sabre/dav/CVE-2014-2055.yaml
- https://github.com/fruux/sabre-dav/releases/tag/1.7.11
