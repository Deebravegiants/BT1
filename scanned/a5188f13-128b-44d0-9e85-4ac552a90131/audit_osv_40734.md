# [M] Lemmy: Rate limit bypass via X-Forwarded-For header spoofing in actix-web ConnectionInfo

## Summary
Severity: Medium
Advisory: CVE-2026-54738
Aliases: GHSA-2hrg-7x4g-9vpg
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:L)
Published: 2026-08-19
Source: https://osv.dev/vulnerability/CVE-2026-54738
Type: osv

## Details
Lemmy is a link aggregator and forum for the fediverse. Prior to 0.19.19 and 1.0.0-beta.1, actix-web ConnectionInfo::realip_remote_addr reads the first value of X-Forwarded-For as the client address used by raw_ip_key in crates/utils/src/rate_limit/mod.rs. Lemmy's bundled docker/nginx.conf uses $proxy_add_x_forwarded_for instead of $remote_addr, which appends the real client address to an X-Forwarded-For value supplied by the client. An unauthenticated attacker can therefore place a different spoofed address first on each request and receive a new rate-limit bucket, bypassing limits on POST /api/v4/account/auth/register, POST /api/v4/account/auth/login, POST /api/v4/post, POST /api/v4/comment, GET /api/v4/search, POST /api/v4/image, and POST /api/v4/account/import_settings. This permits excessive account creation, brute-force attempts, spam, scraping, uploads, and repeated imports. This issue is fixed in versions 0.19.19 and 1.0.0-beta.1.

## References
- https://github.com/LemmyNet/lemmy/releases/tag/0.19.19
- https://github.com/LemmyNet/lemmy/releases/tag/1.0.0-beta.1
- https://join-lemmy.org/news/2026-06-09_-_Lemmy_Release_v0.19.19
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/54xxx/CVE-2026-54738.json
- https://github.com/LemmyNet/lemmy/security/advisories/GHSA-2hrg-7x4g-9vpg
- https://nvd.nist.gov/vuln/detail/CVE-2026-54738
- https://github.com/LemmyNet/lemmy/commit/41513c89ceecee719bff05acfe613e3b1e85f23c
- https://github.com/LemmyNet/lemmy/commit/8b5b2aa78417b53ff3622c01f5bed2f1590f3b82
- https://github.com/LemmyNet/lemmy/pull/6574
- https://github.com/LemmyNet/lemmy/pull/6575
