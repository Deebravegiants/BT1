# [M] SAP HANA Node.js client package vulnerable to Prototype Pollution

## Summary
Severity: Medium
Advisory: GHSA-6339-gv7w-g5f4
CVE: CVE-2024-45277
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2024-10-08
Source: https://github.com/advisories/GHSA-6339-gv7w-g5f4
Type: github-advisory

## Affected
- npm: `@sap/hana-client` — affected >=2.0.0 <2.21.31

## Details
The SAP HANA Node.js client package versions from 2.0.0 before 2.21.31 is impacted by Prototype Pollution vulnerability allowing an attacker to add arbitrary properties to global object prototypes. This is due to improper user input sanitation when using the nestTables feature causing low impact on the availability of the application. This has no impact on Confidentiality and Integrity.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-45277
- https://me.sap.com/notes/3520100
- https://url.sap/sapsecuritypatchday
- https://www.npmjs.com/package/@sap/hana-client?activeTab=code
