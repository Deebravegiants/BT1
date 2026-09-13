# [C] MyTube has an Authorization Bypass vulnerability

## Summary
Severity: Critical
Advisory: CVE-2026-23837
Aliases: GHSA-cmvj-g69f-8664
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-01-19
Source: https://osv.dev/vulnerability/CVE-2026-23837
Type: osv

## Details
MyTube is a self-hosted downloader and player for several video websites. A vulnerability present in version 1.7.65 and poetntially earlier versions allows unauthenticated users to bypass the mandatory authentication check in the roleBasedAuthMiddleware. By simply not providing an authentication cookie (making req.user undefined), a request is incorrectly passed through to downstream handlers. All users running MyTube with loginEnabled: true are impacted. This flaw allows an attacker to access and modify application settings via /api/settings, change administrative and visitor passwords, and access other protected routes that rely on this specific middleware. The problem is patched in v1.7.66. MyTube maintainers recommend all users upgrade to at least version v1.7.64 immediately to secure their instances. The fix ensures that the middleware explicitly blocks requests if a user is not authenticated, rather than defaulting to next(). Those who cannot upgrade immediately can mitigate risk by restricting network access by usi a firewall or reverse proxy (like Nginx) to restrict access to the /api/ endpoints to trusted IP addresses only or, if they are comfortable editing the source code, manually patch by locating roleBasedAuthMiddleware and ensuring that the logic defaults to an error (401 Unauthorized) when req.user is undefined, instead of calling next().

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23837.json
- https://github.com/franklioxygen/MyTube/security/advisories/GHSA-cmvj-g69f-8664
- https://nvd.nist.gov/vuln/detail/CVE-2026-23837
- https://github.com/franklioxygen/MyTube/commit/f85ae9b0d6e4a6480c6af5b675a99069d08d496e
