# [H] SAP Approuter has an Open Redirect vulnerability

## Summary
Severity: High
Advisory: GHSA-44p5-3m5g-vfhj
CVE: CVE-2026-44745
CWE: CWE-601
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-07-14
Source: https://github.com/advisories/GHSA-44p5-3m5g-vfhj
Type: github-advisory

## Affected
- npm: `@sap/approuter` — affected >=0 <21.2.0

## Details
SAP Approuter does not properly validate incoming request headers during the OAuth2 login flow under certain configurations. This allows an unauthenticated remote attacker to craft a malicious link which, when clicked by a victim, could lead to unauthorized access. Successful exploitation results in a high impact to the confidentiality and integrity with no impact on the availability of the application.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-44745
- https://me.sap.com/notes/3741519
- https://url.sap/sapsecuritypatchday
