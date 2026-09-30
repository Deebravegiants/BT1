# [H] UptimeFlare: Montior config / Credentials in `workerConfig` exposed in client-side JavaScript bundle

## Summary
Severity: High
Advisory: CVE-2026-29779
Aliases: GHSA-36q9-v7p3-vj6v
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-03-07
Source: https://osv.dev/vulnerability/CVE-2026-29779
Type: osv

## Details
UptimeFlare is a serverless uptime monitoring & status page solution, powered by Cloudflare Workers. Prior to commit 377a596, configuration file uptime.config.ts exports both pageConfig (safe for client use) and workerConfig (server-only, contains sensitive data) from the same module. Due to pages/incidents.tsx importing and using workerConfig directly inside client-side component code, the entire workerConfig object was included in the client-side JavaScript bundle served to all visitors. This issue has been patched via commit 377a596.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/29xxx/CVE-2026-29779.json
- https://github.com/lyc8503/UptimeFlare/security/advisories/GHSA-36q9-v7p3-vj6v
- https://nvd.nist.gov/vuln/detail/CVE-2026-29779
- https://github.com/lyc8503/UptimeFlare/issues/198
- https://github.com/lyc8503/UptimeFlare/commit/377a5963c66ba9a798abebfe8d80378b053435e9
