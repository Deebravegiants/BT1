# [H] Authentication bypass in @sap/approuter

## Summary
Severity: High
Advisory: GHSA-cpfx-964w-4jvp
CVE: CVE-2025-24876
CWE: CWE-601
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2025-02-11
Source: https://github.com/advisories/GHSA-cpfx-964w-4jvp
Type: github-advisory

## Affected
- npm: `@sap/approuter` — affected >=2.6.1 <16.7.2

## Details
The SAP Approuter Node.js package version v16.7.1 and before is vulnerable to Authentication bypass. When trading an authorization code, an attacker can steal the session of the victim by injecting malicious payload, causing High impact on confidentiality and integrity of the application.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-24876
- https://me.sap.com/notes/3567974
- https://support.sap.com/en/my-support/knowledge-base/security-notes-news/february-2025.html
- https://www.npmjs.com/package/@sap/approuter?activeTab=versions
