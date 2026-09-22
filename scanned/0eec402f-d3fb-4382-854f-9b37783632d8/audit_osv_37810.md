# [H] LORIS has a SQL injection in MRI feedback popup

## Summary
Severity: High
Advisory: CVE-2026-33350
Aliases: GHSA-9r29-6jgc-3ggh
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-04-08
Source: https://osv.dev/vulnerability/CVE-2026-33350
Type: osv

## Details
LORIS (Longitudinal Online Research and Imaging System) is a self-hosted web application that provides data- and project-management for neuroimaging research. Prior to 27.0.3 and 28.0.1, a SQL injection has been identified in some code sections for the MRI feedback popup window of the imaging browser. Attackers can use SQL ingestion to access/alter data on the server. This vulnerability is fixed in 27.0.3 and 28.0.1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33350.json
- https://github.com/aces/Loris/security/advisories/GHSA-9r29-6jgc-3ggh
- https://nvd.nist.gov/vuln/detail/CVE-2026-33350
