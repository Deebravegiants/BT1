# [H] Symlink Arbitrary File Overwrite in bower

## Summary
Severity: High
Advisory: GHSA-p6mr-pxg4-68hx
CVE: CVE-2019-5484
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2019-09-17
Source: https://github.com/advisories/GHSA-p6mr-pxg4-68hx
Type: github-advisory

## Affected
- npm: `bower` — affected >=0 <1.8.8

## Details
Versions of `bower` prior to 1.8.8 are affected by an arbitrary file write vulnerability. The vulnerability occurs because `bower` does not verify that extracted symbolic links do not resolve to targets outside of the extraction root directory.



## Recommendation

Update to version 1.8.8 or later

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-5484
- https://github.com/bower/bower/commit/45c6bfa86f6e57731b153baca9e0b41a1cc699e3
- https://hackerone.com/reports/473811
- https://github.com/nodejs/security-wg/blob/master/vuln/npm/487.json
- https://lists.apache.org/thread.html/r8ba4c628fba7181af58817d452119481adce4ba92e889c643e4c7dd3@%3Ccommits.netbeans.apache.org%3E
- https://lists.apache.org/thread.html/rb5ac16fad337d1f3bb7079549f97d8166d0ef3082629417c39f12d63@%3Cnotifications.netbeans.apache.org%3E
- https://snyk.io/blog/severe-security-vulnerability-in-bowers-zip-archive-extraction
- https://www.npmjs.com/advisories/776
