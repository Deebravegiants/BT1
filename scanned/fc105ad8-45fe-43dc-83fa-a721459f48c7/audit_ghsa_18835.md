# [M] VaahCMS is vulnerable to XSS through its Avatar Upload endpoint

## Summary
Severity: Medium
Advisory: GHSA-q769-phqg-263r
CVE: CVE-2025-61183
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2025-10-08
Source: https://github.com/advisories/GHSA-q769-phqg-263r
Type: github-advisory

## Affected
- Packagist: `webreinvent/vaahcms` — affected >=0

## Details
Cross-Site Scripting in vaahcms v.2.3.1 allows a remote attacker to execute arbitrary code via upload method in the storeAvatar() method of UserBase.php

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-61183
- https://github.com/webreinvent/vaahcms/issues/301
- https://github.com/thawphone/CVE-2025-61183
- https://github.com/webreinvent/vaahcms
