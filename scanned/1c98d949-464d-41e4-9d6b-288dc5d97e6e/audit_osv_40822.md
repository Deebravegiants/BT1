# [C] Wekan: Header-login IP allowlist bypass via X-Forwarded-For spoofing in Wekan allows unauthenticated full account takeover (incl. admin)

## Summary
Severity: Critical
Advisory: CVE-2026-55652
Aliases: GHSA-jggc-qvfc-jr6x
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-15
Source: https://osv.dev/vulnerability/CVE-2026-55652
Type: osv

## Details
Wekan is open source kanban built with Meteor. Prior to 9.46, header-login with HEADER_LOGIN_TRUSTED_IPS uses getRequestIp() in server/lib/headerLoginAuth.js to trust the client-supplied X-Forwarded-For header before the real socket address, allowing an unauthenticated attacker to send HEADER_LOGIN_ID for any username and receive a meteor_login_token session, including for admin. This issue is fixed in version 9.46.

## References
- https://github.com/wekan/wekan/releases/tag/v9.46
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/55xxx/CVE-2026-55652.json
- https://github.com/wekan/wekan/security/advisories/GHSA-jggc-qvfc-jr6x
- https://nvd.nist.gov/vuln/detail/CVE-2026-55652
- https://github.com/wekan/wekan/commit/b181889a565254bc9bf79379a34fc7f617ccda28
