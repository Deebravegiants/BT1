# [H] JumpServer session replays download without authentication

## Summary
Severity: High
Advisory: CVE-2023-42442
Aliases: GHSA-633x-3f4f-v9rw
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:H)
Published: 2023-09-15
Source: https://osv.dev/vulnerability/CVE-2023-42442
Type: osv

## Details
JumpServer is an open source bastion host and a professional operation and maintenance security audit system. Starting in version 3.0.0 and prior to versions 3.5.5 and 3.6.4, session replays can download without authentication. Session replays stored in S3, OSS, or other cloud storage are not affected. The api `/api/v1/terminal/sessions/` permission control is broken and can be accessed anonymously. SessionViewSet permission classes set to `[RBACPermission | IsSessionAssignee]`, relation is or, so any permission matched will be allowed. Versions 3.5.5 and 3.6.4 have a fix. After upgrading, visit the api `$HOST/api/v1/terminal/sessions/?limit=1`. The expected http response code is 401 (`not_authenticated`).

## References
- https://github.com/jumpserver/jumpserver/blob/v3.6.1/apps/terminal/api/session/session.py#L91
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/42xxx/CVE-2023-42442.json
- https://github.com/jumpserver/jumpserver/security/advisories/GHSA-633x-3f4f-v9rw
- https://nvd.nist.gov/vuln/detail/CVE-2023-42442
- https://github.com/jumpserver/jumpserver/commit/0a58bba59cd275bab8e0ae58bf4b359fbc5eb74a
