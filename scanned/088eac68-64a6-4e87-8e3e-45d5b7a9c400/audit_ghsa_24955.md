# [M] Mediawiki information disclosure vulnerability

## Summary
Severity: Medium
Advisory: GHSA-hr8v-f4g2-p66f
CVE: CVE-2018-0504
CWE: CWE-532
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-hr8v-f4g2-p66f
Type: github-advisory

## Affected
- Packagist: `mediawiki/core` — affected >=1.27.0 <1.27.5
- Packagist: `mediawiki/core` — affected >=1.29.0 <1.29.3
- Packagist: `mediawiki/core` — affected >=1.30.0 <1.30.1
- Packagist: `mediawiki/core` — affected >=1.31.0 <1.31.1

## Details
Mediawiki 1.31 before 1.31.1, 1.30.1, 1.29.3 and 1.27.5 contains an information disclosure flaw in the Special:Redirect/logid

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-0504
- https://access.redhat.com/errata/RHSA-2019:3238
- https://access.redhat.com/errata/RHSA-2019:3813
- https://github.com/FriendsOfPHP/security-advisories/blob/master/mediawiki/core/CVE-2018-0504.yaml
- https://github.com/wikimedia/mediawiki
- https://lists.wikimedia.org/pipermail/wikitech-l/2018-September/090849.html
- https://phabricator.wikimedia.org/T187638
- https://www.debian.org/security/2018/dsa-4301
- http://www.securitytracker.com/id/1041695
