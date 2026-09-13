# [M] Horilla: Unauthorized Helpdesk Attachment Access via Attachment ID Manipulation

## Summary
Severity: Medium
Advisory: CVE-2026-40867
Aliases: GHSA-j6qp-j853-qrff
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-04-21
Source: https://osv.dev/vulnerability/CVE-2026-40867
Type: osv

## Details
Horilla is a free and open source Human Resource Management System (HRMS). In 1.5.0, a broken access control vulnerability in the helpdesk attachment viewer allows any authenticated user to view attachments from other tickets by changing the attachment ID. This can expose sensitive support files and internal documents across unrelated users or teams.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40867.json
- https://github.com/horilla/horilla-hr/security/advisories/GHSA-j6qp-j853-qrff
- https://nvd.nist.gov/vuln/detail/CVE-2026-40867
