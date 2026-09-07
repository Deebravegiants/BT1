# [M] MediaWiki allows a denial of service

## Summary
Severity: Medium
Advisory: GHSA-c8wv-qwwc-6j73
CVE: CVE-2021-41800
CWE: CWE-770
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-c8wv-qwwc-6j73
Type: github-advisory

## Affected
- Packagist: `mediawiki/core` — affected >=0 <1.36.2

## Details
MediaWiki before 1.36.2 allows a denial of service (resource consumption because of lengthy query processing time). Visiting Special:Contributions can sometimes result in a long running SQL query because PoolCounter protection is mishandled.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-41800
- https://github.com/wikimedia/mediawiki/commit/781caf83dba90c18349f930bbaaa0e89f003f874
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/CJDYJQWT43GBD6GNQ4OW7JOZ6WQ6DZTN
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/MDBPECBWN6LWNSWIQMVXK6PP4YFEUYHA
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/QNEAI2T3Y65I55ZB6UE6RMC662RZTGRX
- https://lists.wikimedia.org/hyperkitty/list/wikitech-l@lists.wikimedia.org/thread/2IFS5CM2YV4VMSODPX3J2LFHKSEWVFV5
- https://phabricator.wikimedia.org/T284419
- https://security.gentoo.org/glsa/202305-24
