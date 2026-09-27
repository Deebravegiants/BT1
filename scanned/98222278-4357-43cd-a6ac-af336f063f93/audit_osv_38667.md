# [M] Password Pusher: JSON API `/p.json` file upload alias bypasses file-push authentication

## Summary
Severity: Medium
Advisory: CVE-2026-41308
Aliases: GHSA-qfh8-f79c-x86c
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:L)
Published: 2026-05-08
Source: https://osv.dev/vulnerability/CVE-2026-41308
Type: osv

## Details
Password Pusher is an open source application to communicate sensitive information over the web. Prior to versions 1.69.3 and 2.4.2, a security issue in OSS PasswordPusher allowed unauthenticated creation of file-type pushes through a generic JSON API create path under certain configurations. This could bypass the intended authentication boundary for file push creation. This issue has been patched in versions 1.69.3 and 2.4.2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/41xxx/CVE-2026-41308.json
- https://github.com/pglombardo/PasswordPusher/security/advisories/GHSA-qfh8-f79c-x86c
- https://nvd.nist.gov/vuln/detail/CVE-2026-41308
- https://github.com/pglombardo/PasswordPusher/commit/45dc2512875231ef45ecd5dfc8c3c8185f882bf4
- https://github.com/pglombardo/PasswordPusher/pull/4381
