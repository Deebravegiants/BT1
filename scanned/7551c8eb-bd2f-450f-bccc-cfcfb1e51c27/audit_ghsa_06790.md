# [C] SAP Approuter Vulnerable to HTTP Request Smuggling

## Summary
Severity: Critical
Advisory: GHSA-8m85-wqg7-c529
CVE: CVE-2026-27690
CWE: CWE-444
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H (CVSS_V3)
Published: 2026-07-14
Source: https://github.com/advisories/GHSA-8m85-wqg7-c529
Type: github-advisory

## Affected
- npm: `@sap/approuter` — affected >=0 <20.10.0

## Details
Due to an HTTP Request Smuggling vulnerability in SAP Approuter, an unauthenticated attacker could send a specially crafted HTTP request that leads to request-response desynchronization. This could result in the exposure of user responses and cause the system to become unavailable. This leads to a high impact on confidentiality and availability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-27690
- https://me.sap.com/notes/3720138
- https://url.sap/sapsecuritypatchday
