# [H] Google Sheets OAuth access token disclosure to guest members via getAccessToken

## Summary
Severity: High
Advisory: CVE-2026-48767
Aliases: GHSA-qjpp-9cqc-jhh8
CVSS: 7.6 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:L)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/CVE-2026-48767
Type: osv

## Details
TypeBot is a chatbot builder tool. Versions prior to 3.17.0 allow a low-privilege guest member of a workspace to obtain a live Google Sheets OAuth access token for that workspace by calling the Google Sheets helper `getAccessToken`. The vulnerable path checks only whether the caller has read access to the workspace, decrypts the stored Google OAuth credential, refreshes or retrieves the access token through the Google client, and returns the raw bearer token directly to the caller. Because guest members can also enumerate credential identifiers, a guest can mint and reuse the workspace's Google access token outside Typebot. Version 3.17.0 patches the issue.

## References
- https://github.com/baptisteArno/typebot.io/releases/tag/v3.17.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/48xxx/CVE-2026-48767.json
- https://github.com/baptisteArno/typebot.io/security/advisories/GHSA-qjpp-9cqc-jhh8
- https://nvd.nist.gov/vuln/detail/CVE-2026-48767
- https://github.com/baptisteArno/typebot.io/commit/c0ffd825e2f4ee2256a157fd085fb624dcede625
- https://github.com/baptisteArno/typebot.io/pull/2501
