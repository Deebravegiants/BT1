# [M] Cross-Site Scripting in webtorrent

## Summary
Severity: Medium
Advisory: GHSA-gjh4-fcv3-whpq
CVE: CVE-2019-15782
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2019-09-04
Source: https://github.com/advisories/GHSA-gjh4-fcv3-whpq
Type: github-advisory

## Affected
- npm: `webtorrent` — affected >=0 <0.107.6

## Details
Versions of `webtorrent` prior to 0.107.6 are vulnerable to Cross-Site Scripting. `webtorrent` servers started with `torrent.createServer()` lists a torrent's title and files in the index page without sanitization. This allows attackers to execute arbitrary JavaScript in the victim's browser through files with names containing the malicious payload. The issue is mitigated due to the fact that the server only allows fetching data pieces from the torrent.


## Recommendation

Upgrade to version 0.107.6 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-15782
- https://github.com/webtorrent/webtorrent/pull/1714
- https://github.com/webtorrent/webtorrent/commit/7e829b5d52c32d2e6d8f5fbcf0f8f418fffde083
- https://hackerone.com/reports/681617
- https://github.com/webtorrent/webtorrent/compare/v0.107.5...v0.107.6
- https://snyk.io/vuln/SNYK-JS-WEBTORRENT-460351
- https://www.npmjs.com/advisories/1158
