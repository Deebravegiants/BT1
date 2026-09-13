# [M] Open WebUI: Admin demoted through SSO role sync keeps read and write access to all users' notes

## Summary
Severity: Medium
Advisory: CVE-2026-87014
Aliases: GHSA-wjwr-xfp9-r66p
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-09-09
Source: https://osv.dev/vulnerability/CVE-2026-87014
Type: osv

## Details
Open WebUI is an extensible, feature-rich, and user-friendly self-hosted AI platform. From 0.9.0 until 0.11.1, role synchronization in backend/open_webui/routers/auths.py and backend/open_webui/utils/oauth.py updated an administrator's database role without invalidating the user record cached by backend/open_webui/socket/main.py. An administrator demoted through a trusted role header or OAuth role mapping could keep an already-open Socket.IO connection and continue reading or editing every user's collaborative notes until that connection closed. This issue is fixed in version 0.11.1.

## References
- https://github.com/open-webui/open-webui/releases/tag/v0.11.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/87xxx/CVE-2026-87014.json
- https://github.com/open-webui/open-webui/security/advisories/GHSA-wjwr-xfp9-r66p
- https://nvd.nist.gov/vuln/detail/CVE-2026-87014
- https://github.com/open-webui/open-webui/commit/ce3c175e260709f359d7e6cbb3132f0572098b95
