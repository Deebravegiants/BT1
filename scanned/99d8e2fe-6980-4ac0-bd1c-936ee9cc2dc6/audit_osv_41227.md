# [M] ChurchCRM has Reflected Cross-Site Scripting (XSS) via unsanitized request parameter names and values

## Summary
Severity: Medium
Advisory: CVE-2026-58411
Aliases: GHSA-p6j6-vrpg-4pp8
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:H/VI:L/VA:N/SC:L/SI:L/SA:N)
Published: 2026-07-13
Source: https://osv.dev/vulnerability/CVE-2026-58411
Type: osv

## Details
ChurchCRM is an open-source church management system. Prior to version 7.4.0, Cross-Site Scripting (XSS) vulnerabilities were identified due to insufficient output encoding of user-controlled request parameter names and parameter values. The application reflects attacker-controlled input into JavaScript string contexts and HTML attribute contexts without proper sanitization or contextual output encoding. Affected endpoints observed during testing: /FamilyCustomFieldsEditor.php, /PaddleNumList.php and /admin/system/church-info. Potential consequences include session-token theft, account takeover, unauthorized actions on behalf of authenticated users, exposure of sensitive church member information, credential harvesting, phishing, and privilege escalation when administrators are targeted. This issue has been resolved in version 7.4.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/58xxx/CVE-2026-58411.json
- https://github.com/ChurchCRM/CRM/security/advisories/GHSA-p6j6-vrpg-4pp8
- https://nvd.nist.gov/vuln/detail/CVE-2026-58411
