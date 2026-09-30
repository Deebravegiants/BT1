# [H] Rocket.Chat: Any Authenticated User Can Permanently Deregister Workspace from Rocket.Chat Cloud via Unprotected `/api/v1/fingerprint` Endpoint

## Summary
Severity: High
Advisory: CVE-2026-55762
Aliases: GHSA-8hhc-j325-rxqp
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-55762
Type: osv

## Details
Rocket.Chat is an open-source, secure, fully customizable communications platform. Prior to 8.5.1, 8.4.4, 8.3.6, 8.2.6, 8.1.6, 8.0.7, and 7.10.13, the POST /api/v1/fingerprint REST endpoint enforces authentication (authRequired: true) but performs no authorization check. Any authenticated user — including a standard user role account — can call this endpoint with {"setDeploymentAs": "new-workspace"} to permanently deregister the workspace from Rocket.Chat Cloud. This wipes all cloud credentials, removes the workspace license, breaks push notifications for all users, and requires manual re-registration to recover. This vulnerability is fixed in 8.5.1, 8.4.4, 8.3.6, 8.2.6, 8.1.6, 8.0.7, and 7.10.13.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/55xxx/CVE-2026-55762.json
- https://github.com/RocketChat/Rocket.Chat/security/advisories/GHSA-8hhc-j325-rxqp
- https://nvd.nist.gov/vuln/detail/CVE-2026-55762
