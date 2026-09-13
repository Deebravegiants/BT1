# [C] Prototype pollution in Plist before 3.0.5 can cause denial of service

## Summary
Severity: Critical
Advisory: GHSA-4cpg-3vgw-4877
CVE: CVE-2022-22912
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-02-18
Source: https://github.com/advisories/GHSA-4cpg-3vgw-4877
Type: github-advisory

## Affected
- npm: `plist` — affected >=0 <3.0.5

## Details
Prototype pollution vulnerability via `.parse()` in Plist allows attackers to cause a Denial of Service (DoS) and may lead to remote code execution.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-22912
- https://github.com/TooTallNate/plist.js/issues/114
- https://github.com/TooTallNate/plist.js/pull/118
- https://github.com/TooTallNate/plist.js/commit/96e2303d059e6be0c9e0c4773226d14b4758de52
- https://github.com/TooTallNate/plist.js
