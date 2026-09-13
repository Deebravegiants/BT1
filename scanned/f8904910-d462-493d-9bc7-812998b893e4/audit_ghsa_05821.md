# [H] SAP Approuter has an Information Disclosure vulnerability

## Summary
Severity: High
Advisory: GHSA-vhh6-v828-x62f
CVE: CVE-2026-58230
CWE: CWE-601
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:L/A:L (CVSS_V3)
Published: 2026-08-11
Source: https://github.com/advisories/GHSA-vhh6-v828-x62f
Type: github-advisory

## Affected
- npm: `@sap/approuter` — affected >=0 <23.0.0

## Details
SAP Approuter does not sufficiently validate certain token content under specific configurations. An unauthenticated attacker could send a specially crafted token to cause sensitive credential material to be sent to an attacker-controlled destination. The attack complexity is high due to non-default preconditions required in the target environment. This results in a high impact on confidentiality and a low impact on integrity and availability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-58230
- https://me.sap.com/notes/3786038
- https://url.sap/sapsecuritypatchday
