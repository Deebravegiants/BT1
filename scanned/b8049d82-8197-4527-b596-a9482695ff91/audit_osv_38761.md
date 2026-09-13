# [H] TypeBot has Authorization Bypass in Google Sheets `getSheets` Endpoint that Allows Cross-Workspace Credential Access

## Summary
Severity: High
Advisory: CVE-2026-42142
Aliases: GHSA-7jr4-r73c-h4h9
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/CVE-2026-42142
Type: osv

## Details
TypeBot is a chatbot builder tool. Prior to version 3.17.0, the `handleGetSheets` API handler (`POST /api/sheets/getSheets`) does not validate workspace membership, allowing any authenticated user to access and decrypt another workspace's Google Sheets OAuth credentials and retrieve spreadsheet data (sheet names, IDs, column headers). Version 3.17.0 fixes the issue.

## References
- https://github.com/baptisteArno/typebot.io/releases/tag/v3.17.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/42xxx/CVE-2026-42142.json
- https://github.com/baptisteArno/typebot.io/security/advisories/GHSA-7jr4-r73c-h4h9
- https://nvd.nist.gov/vuln/detail/CVE-2026-42142
- https://github.com/baptisteArno/typebot.io/commit/91d2a986d942232b98c066fc460d7c48c04a464b
- https://github.com/baptisteArno/typebot.io/pull/2467
