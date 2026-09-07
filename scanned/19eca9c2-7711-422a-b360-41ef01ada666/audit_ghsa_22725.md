# [M] eZ Publish Cross-site Scripting (XSS) vulnerability

## Summary
Severity: Medium
Advisory: GHSA-m98q-p5gq-q5ff
CVE: CVE-2017-1000431
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-m98q-p5gq-q5ff
Type: github-advisory

## Affected
- Packagist: `ezsystems/ezpublish-legacy` — affected >=5.4.0 <5.4.10
- Packagist: `ezsystems/ezpublish-legacy` — affected >=5.3.0 <5.3.12.1

## Details
eZ Systems eZ Publish version 5.4.0 to 5.4.9, and 5.3.12.0 and older, is vulnerable to an XSS issue in the search module, resulting in a risk of attackers injecting scripts which may e.g. steal authentication credentials.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-1000431
- https://github.com/ezsystems/ezpublish-legacy/commit/c7174295fa0b9bd81bd4af908082464b0b80f278
- https://github.com/FriendsOfPHP/security-advisories/blob/master/ezsystems/ezpublish-legacy/CVE-2017-1000431.yaml
- https://web.archive.org/web/20210408035246/http://share.ez.no/community-project/security-advisories/ezsa-2017-005-xss-issue-in-search
- http://share.ez.no/community-project/security-advisories/ezsa-2017-005-xss-issue-in-search
