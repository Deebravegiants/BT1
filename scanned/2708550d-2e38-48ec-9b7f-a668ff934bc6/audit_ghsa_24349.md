# [M] Wikimedia Parsoid vulnerable to Cross-site Scripting (XSS)

## Summary
Severity: Medium
Advisory: GHSA-5pqx-77vf-85rw
CVE: CVE-2021-30458
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-5pqx-77vf-85rw
Type: github-advisory

## Affected
- Packagist: `wikimedia/parsoid` — affected >=0.12 <0.12.2
- Packagist: `wikimedia/parsoid` — affected >=0 <0.11.1

## Details
An issue was discovered in Wikimedia Parsoid before 0.11.1 and 0.12.x before 0.12.2. An attacker can send crafted wikitext that Utils/WTUtils.php will transform by using a <meta> tag, bypassing sanitization steps, and potentially allowing for XSS.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-30458
- https://github.com/FriendsOfPHP/security-advisories/blob/master/wikimedia/parsoid/CVE-2021-30458.yaml
- https://github.com/wikimedia/mediawiki-services-parsoid
- https://phabricator.wikimedia.org/T279451
- https://security.gentoo.org/glsa/202107-40
- https://www.mediawiki.org/wiki/Parsoid
