# [M] img_auth.php may leak private extension images into the public cache

## Summary
Severity: Medium
Advisory: GHSA-xpv7-93cm-4mxv
CVE: CVE-2020-15005
CWE: CWE-200
Ecosystem: Packagist
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-xpv7-93cm-4mxv
Type: github-advisory

## Affected
- Packagist: `mediawiki/core` — affected >=0 <1.31.8
- Packagist: `mediawiki/core` — affected >=1.32.0 <1.33.4
- Packagist: `mediawiki/core` — affected >=1.34.0 <1.34.2

## Details
In MediaWiki before 1.31.8, 1.32.x and 1.33.x before 1.33.4, and 1.34.x before 1.34.2, private wikis behind a caching server using the img_auth.php image authorization security feature may have had their files cached publicly, so any unauthorized user could view them. This occurs because Cache-Control and Vary headers were mishandled.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-15005
- https://gerrit.wikimedia.org/r/plugins/gitiles/mediawiki/core/+/REL1_31/RELEASE-NOTES-1.31
- https://gerrit.wikimedia.org/r/plugins/gitiles/mediawiki/core/+/REL1_33/RELEASE-NOTES-1.33
- https://gerrit.wikimedia.org/r/plugins/gitiles/mediawiki/core/+/REL1_34/RELEASE-NOTES-1.34
- https://github.com/wikimedia/mediawiki
- https://lists.debian.org/debian-lts-announce/2020/12/msg00034.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/EEZIMLJMJS72SJXPYL736XMUAVCRQD2H
- https://lists.wikimedia.org/pipermail/wikitech-l/2020-June/093535.html
- https://phabricator.wikimedia.org/T248947
- https://www.debian.org/security/2020/dsa-4767
