# [C] rclone serve s3: --auth-proxy without --auth-key authenticates nobody - full SigV4 signature bypass

## Summary
Severity: Critical
Advisory: CVE-2026-88018
Aliases: GHSA-xwwr-4h3p-r22c
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-09-10
Source: https://osv.dev/vulnerability/CVE-2026-88018
Type: osv

## Details
rclone is a command-line program to sync files and directories to and from different cloud storage providers. Prior to 1.75.1, rclone serve s3 configured with --auth-proxy but without --auth-key allows authPairMiddleware to register any client-chosen accessKeyID with an empty ws.s3Secret. gofakes3 then verifies the request’s SigV4 signature against that same empty secret, while Server.auth passes the access key identifier as both the user and authentication value to the proxy without an independent per-identity secret. An unauthenticated network attacker can therefore choose an arbitrary access key, sign with an empty secret, and reach whatever backend the auth-proxy script resolves for that identity. This issue is fixed in version 1.75.1.

## References
- https://github.com/rclone/rclone/releases/tag/v1.75.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/88xxx/CVE-2026-88018.json
- https://github.com/rclone/rclone/security/advisories/GHSA-xwwr-4h3p-r22c
- https://nvd.nist.gov/vuln/detail/CVE-2026-88018
- https://github.com/rclone/rclone/commit/90595f34f27f569be6b27c57fe5ab65057d323bd
