# [M] Typebot: IDOR in Result Logs Endpoint Allows Cross-Workspace Data Disclosure

## Summary
Severity: Medium
Advisory: CVE-2026-28444
Aliases: GHSA-c63p-mqx5-75r7
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-05-22
Source: https://osv.dev/vulnerability/CVE-2026-28444
Type: osv

## Details
Typebot is a chatbot builder tool. In versions 3.15.2 and prior, the getResultLogs API endpoint authorizes the caller against the provided typebotId but fetches logs solely by resultId without verifying that the result belongs to the authorized typebot, leading to IDOR. An authenticated attacker can supply their own typebotId alongside any victim's resultId to read execution logs from other workspaces, leaking sensitive data including HTTP response bodies, AI model outputs, and webhook payloads. Every other result-scoped endpoint in the same router properly validates that the resultId belongs to the authorized typebotId. This confirms the missing check is an oversight, not a design choice. This issue has been fixed in version 3.15.2.

## References
- https://github.com/baptisteArno/typebot.io/releases/tag/v3.16.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/28xxx/CVE-2026-28444.json
- https://github.com/baptisteArno/typebot.io/security/advisories/GHSA-c63p-mqx5-75r7
- https://nvd.nist.gov/vuln/detail/CVE-2026-28444
- https://github.com/baptisteArno/typebot.io/commit/d82b2d47c86ae614a08d4073c669ca64442faff2
