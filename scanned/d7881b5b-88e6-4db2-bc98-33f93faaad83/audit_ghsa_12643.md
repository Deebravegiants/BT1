# [M] MediaWiki Cross-site Scripting vulnerability

## Summary
Severity: Medium
Advisory: GHSA-fmrf-p77g-vv5c
CVE: CVE-2023-37302
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-06-30
Source: https://github.com/advisories/GHSA-fmrf-p77g-vv5c
Type: github-advisory

## Affected
- Packagist: `wikibase/wikibase` — affected >=0

## Details
An issue was discovered in SiteLinksView.php in Wikibase in MediaWiki through 1.39.3. There is XSS via a crafted badge title attribute. This is also related to lack of escaping in wbTemplate (from resources/wikibase/templates.js) for quotes (which can be in a title attribute).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-37302
- https://gerrit.wikimedia.org/r/c/mediawiki/extensions/Wikibase/+/933649
- https://gerrit.wikimedia.org/r/c/mediawiki/extensions/Wikibase/+/933650
- https://github.com/wikimedia/mediawiki
- https://phabricator.wikimedia.org/T339111
