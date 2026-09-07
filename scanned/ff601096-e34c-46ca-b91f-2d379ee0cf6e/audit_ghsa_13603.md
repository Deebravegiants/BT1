# [H] MediaWiki Denial of Service vulnerability

## Summary
Severity: High
Advisory: GHSA-w5fx-cx7f-6vr9
CVE: CVE-2023-45363
CWE: CWE-835
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-10-09
Source: https://github.com/advisories/GHSA-w5fx-cx7f-6vr9
Type: github-advisory

## Affected
- Packagist: `mediawiki/core` — affected >=0 <1.35.12
- Packagist: `mediawiki/core` — affected >=1.36.0 <1.39.5
- Packagist: `mediawiki/core` — affected >=1.40.0 <1.40.1

## Details
An issue was discovered in ApiPageSet.php in MediaWiki before 1.35.12, 1.36.x through 1.39.x before 1.39.5, and 1.40.x before 1.40.1. It allows attackers to cause a denial of service (unbounded loop and RequestTimeoutException) when querying pages redirected to other variants with redirects and converttitles set.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-45363
- https://github.com/wikimedia/mediawiki/commit/24c3ef2474c6daa20ed48168d46196a55346dfd8
- https://github.com/wikimedia/mediawiki
- https://lists.debian.org/debian-lts-announce/2023/11/msg00027.html
- https://phabricator.wikimedia.org/T333050
- https://www.debian.org/security/2023/dsa-5520
