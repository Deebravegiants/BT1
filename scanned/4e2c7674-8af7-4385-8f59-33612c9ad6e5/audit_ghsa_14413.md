# [M] rsshub vulnerable to Cross-site Scripting via unvalidated URL parameters

## Summary
Severity: Medium
Advisory: GHSA-32gr-4cq6-5w5q
CVE: CVE-2023-26491
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-03-01
Source: https://github.com/advisories/GHSA-32gr-4cq6-5w5q
Type: github-advisory

## Affected
- npm: `rsshub` — affected >=0 <1.0.0-master.c910c4d

## Details
### Impact

When the URL parameters contain certain special characters, it returns an error page that does not properly handle XSS vulnerabilities, allowing for the execution of arbitrary JavaScript code.

Users who access the deliberately constructed URL are affected.

### Patches

This vulnerability was fixed in version c910c4d28717fb860fbe064736641f379fab2c91. Please upgrade to this or a later version.

### Workarounds

No.

## References
- https://github.com/DIYgod/RSSHub/security/advisories/GHSA-32gr-4cq6-5w5q
- https://nvd.nist.gov/vuln/detail/CVE-2023-26491
- https://github.com/DIYgod/RSSHub/commit/c910c4d28717fb860fbe064736641f379fab2c91
- https://github.com/DIYgod/RSSHub
