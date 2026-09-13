# [H] mongosh vulnerable to local privilege escalation

## Summary
Severity: High
Advisory: GHSA-f5w3-73h4-jpcm
CVE: CVE-2025-1756
CWE: CWE-426
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2025-02-27
Source: https://github.com/advisories/GHSA-f5w3-73h4-jpcm
Type: github-advisory

## Affected
- npm: `mongosh` — affected >=0 <2.3.0

## Details
mongosh may be susceptible to local privilege escalation under certain conditions potentially enabling unauthorized actions on a user's system with elevated privilege, when a crafted file is stored in C:\node_modules\. This issue affects mongosh prior to 2.3.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-1756
- https://access.redhat.com/errata/RHSA-2025:1756
- https://github.com/mongodb-js/mongosh
- https://jira.mongodb.org/browse/MONGOSH-2028
