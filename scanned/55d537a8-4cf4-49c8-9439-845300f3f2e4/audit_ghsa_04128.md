# [C] Code Injection in morgan

## Summary
Severity: Critical
Advisory: GHSA-gwg9-rgvj-4h5j
CVE: CVE-2019-5413
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2019-03-25
Source: https://github.com/advisories/GHSA-gwg9-rgvj-4h5j
Type: github-advisory

## Affected
- npm: `morgan` — affected >=0 <1.9.1

## Details
Verisons of `morgan` before 1.9.1 are vulnerable to code injection when user input is allowed into the filter or combined with a prototype pollution attack.


## Recommendation

Update to version 1.9.1 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-5413
- https://hackerone.com/reports/390881
- https://github.com/advisories/GHSA-gwg9-rgvj-4h5j
- https://github.com/nodejs/security-wg/blob/master/vuln/npm/473.json
- https://lists.apache.org/thread.html/r8ba4c628fba7181af58817d452119481adce4ba92e889c643e4c7dd3@%3Ccommits.netbeans.apache.org%3E
- https://lists.apache.org/thread.html/rb5ac16fad337d1f3bb7079549f97d8166d0ef3082629417c39f12d63@%3Cnotifications.netbeans.apache.org%3E
- https://www.npmjs.com/advisories/736
