# [H] Misskey allows token to remain valid in cookie after signing out

## Summary
Severity: High
Advisory: CVE-2025-24896
Aliases: GHSA-w98m-j6hq-cwjm
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N)
Published: 2025-02-11
Source: https://osv.dev/vulnerability/CVE-2025-24896
Type: osv

## Details
Misskey is an open source, federated social media platform. Starting in version 12.109.0 and prior to version 2025.2.0-alpha.0, a login token named `token` is stored in a cookie for authentication purposes in Bull Dashboard, but this remains undeleted even after logout is performed. The primary affected users will be users who have logged into Misskey using a public PC or someone else's device, but it's possible that users who have logged out of Misskey before lending their PC to someone else could also be affected. Version 2025.2.0-alpha.0 contains a fix for this issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/24xxx/CVE-2025-24896.json
- https://github.com/misskey-dev/misskey/security/advisories/GHSA-w98m-j6hq-cwjm
- https://nvd.nist.gov/vuln/detail/CVE-2025-24896
- https://github.com/misskey-dev/misskey/commit/ba9f295ef2bf31cc90fa587e20b9a7655b7a1824
