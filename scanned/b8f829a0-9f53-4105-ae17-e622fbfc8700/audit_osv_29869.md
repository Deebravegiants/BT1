# [H] CVE-2024-47210

## Summary
Severity: High
Advisory: CVE-2024-47210
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-09-21
Source: https://osv.dev/vulnerability/CVE-2024-47210
Type: osv

## Details
Gladys Assistant before 4.45.1 allows Privilege Escalation (a user changing their own role) because req.body.role can be used in updateMySelf in server/api/controllers/user.controller.js.

## References
- https://github.com/GladysAssistant/Gladys/compare/v4.45.0...v4.45.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/47xxx/CVE-2024-47210.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-47210
- https://github.com/GladysAssistant/Gladys/commit/344ad9b8ca3078d9292dd95f2dd7b9172bc6ebbe
- https://github.com/GladysAssistant/Gladys/pull/2115
