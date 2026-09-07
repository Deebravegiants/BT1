# [M] Open Redirect in trailing-slash

## Summary
Severity: Medium
Advisory: GHSA-rfhr-62xp-2fp2
CVE: CVE-2021-23387
CWE: CWE-601
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2021-06-08
Source: https://github.com/advisories/GHSA-rfhr-62xp-2fp2
Type: github-advisory

## Affected
- npm: `trailing-slash` — affected >=0 <2.0.1

## Details
The package trailing-slash before 2.0.1 are vulnerable to Open Redirect via the use of trailing double slashes in the URL when accessing the vulnerable endpoint (such as https://example.com//attacker.example/). The vulnerable code is in index.js::createTrailing(), as the web server uses relative URLs instead of absolute URLs.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23387
- https://github.com/fardog/trailing-slash/commit/f8e66f1429308247e5a119d430203077d8f05048
- https://github.com/fardog/trailing-slash/blob/f640ece055fe85275c983de5eb94661b95e35670/index.js%23L36
- https://snyk.io/vuln/SNYK-JS-TRAILINGSLASH-1085707
