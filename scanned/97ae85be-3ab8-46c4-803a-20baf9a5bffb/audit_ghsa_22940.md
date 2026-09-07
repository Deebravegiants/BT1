# [M] MediaWiki makeCollapsible allows applying event handler to any CSS selector

## Summary
Severity: Medium
Advisory: GHSA-pfm2-mqwj-ggm5
CVE: CVE-2020-10960
CWE: CWE-116, CWE-74
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-pfm2-mqwj-ggm5
Type: github-advisory

## Affected
- Packagist: `mediawiki/core` — affected >=1.31.0 <1.31.7
- Packagist: `mediawiki/core` — affected >=1.33.0 <1.33.3
- Packagist: `mediawiki/core` — affected >=1.34.0 <1.34.1

## Details
In MediaWiki before 1.34.1, users can add various Cascading Style Sheets (CSS) classes (which can affect what content is shown or hidden in the user interface) to arbitrary DOM nodes via HTML content within a MediaWiki page. This occurs because jquery.makeCollapsible allows applying an event handler to any Cascading Style Sheets (CSS) selector. There is no known way to exploit this for cross-site scripting (XSS).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-10960
- https://github.com/FriendsOfPHP/security-advisories/blob/master/mediawiki/core/CVE-2020-10960.yaml
- https://lists.wikimedia.org/pipermail/wikitech-l/2020-March/093243.html
- https://phabricator.wikimedia.org/T246602
