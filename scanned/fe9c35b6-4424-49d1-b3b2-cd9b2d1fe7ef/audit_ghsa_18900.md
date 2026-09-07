# [M] Clerk-js vulnerable to bypass of OAuth authentication flow by manipulating request at OTP verification stage

## Summary
Severity: Medium
Advisory: GHSA-3mm3-wfpv-q85g
CVE: CVE-2025-63700
CWE: CWE-290, CWE-639
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-11-20
Source: https://github.com/advisories/GHSA-3mm3-wfpv-q85g
Type: github-advisory

## Affected
- npm: `@clerk/clerk-js` — affected >=0

## Details
An issue was discovered in Clerk-js 5.88.0 allowing attackers to bypass the OAuth authentication flow by manipulating the request at the OTP verification stage.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-63700
- https://clerk.com
- https://github.com/clerk/javascript
- https://github.com/itsnishat08/CVE-2025-63700
