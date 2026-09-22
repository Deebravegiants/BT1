# [M] Typebot IDOR Vulnerability: Unauthorized API Token Deletion and Exposure

## Summary
Severity: Medium
Advisory: CVE-2025-64706
Aliases: GHSA-grx8-g27p-8hpp
CVSS: 5.0 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2025-11-13
Source: https://osv.dev/vulnerability/CVE-2025-64706
Type: osv

## Details
Typebot is an open-source chatbot builder. In version 3.9.0 up to but excluding version 3.13.0, an Insecure Direct Object Reference (IDOR) vulnerability exists in the API token management endpoint. An authenticated attacker can delete any user's API token and retrieve its value by simply knowing the target user's ID and token ID, without requiring authorization checks. Version 3.13.0 fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/64xxx/CVE-2025-64706.json
- https://github.com/baptisteArno/typebot.io/security/advisories/GHSA-grx8-g27p-8hpp
- https://nvd.nist.gov/vuln/detail/CVE-2025-64706
