# [C] Escalation of privileges in @sap/xssec

## Summary
Severity: Critical
Advisory: GHSA-p2vx-qj66-88q3
CVE: CVE-2023-49583
CWE: CWE-269, CWE-639, CWE-749
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2023-12-12
Source: https://github.com/advisories/GHSA-p2vx-qj66-88q3
Type: github-advisory

## Affected
- npm: `@sap/xssec` — affected >=0 <3.6.0

## Details
SAP BTP Security Services Integration Library ([Node.js] @sap/xssec - versions < 3.6.0, allow under certain conditions an escalation of privileges. On successful exploitation, an unauthenticated attacker can obtain arbitrary permissions within the application.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-49583
- https://blogs.sap.com/2023/12/12/unveiling-critical-security-updates-sap-btp-security-note-3411067
- https://me.sap.com/notes/3411067
- https://me.sap.com/notes/3412456
- https://me.sap.com/notes/3413475
- https://www.npmjs.com/package/@sap/xssec
- https://www.sap.com/documents/2022/02/fa865ea4-167e-0010-bca6-c68f7e60039b.html
