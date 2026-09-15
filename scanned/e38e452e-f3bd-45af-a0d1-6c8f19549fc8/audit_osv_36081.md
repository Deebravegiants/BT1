# [H] Use of hard-coded credentials in Prospero Flow CRM employee onboarding

## Summary
Severity: High
Advisory: CVE-2026-19871
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-14
Source: https://osv.dev/vulnerability/CVE-2026-19871
Type: osv

## Details
Use of Hard-coded Credentials in the human resources component in Roskus Prospero Flow CRM before 5.15.9 allows unauthenticated remote attackers to authenticate as any employee onboarded through the standard flow, knowing only their email address, because the employee save controller falls back to the literal password "changeme" and the onboarding form provides no password field.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/19xxx/CVE-2026-19871.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-19871
- https://github.com/Roskus/prospero-flow-crm/commit/5cc01ed958db4ad0a026a8daa1c6a8bb98a43e66
- https://github.com/Roskus/prospero-flow-crm
- https://secur0.com/en/cna/cve-list/cve-2026-19871-hardcoded-credentials-in-prospero-flow-crm-employee-onboarding
