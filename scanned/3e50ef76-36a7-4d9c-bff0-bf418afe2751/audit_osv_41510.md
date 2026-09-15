# [M] bunkerweb: Read-only Web UI users can delete job cache files due to missing authorization on /cache/ routes

## Summary
Severity: Medium
Advisory: CVE-2026-61718
Aliases: GHSA-q7rm-935c-v39g
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:L)
Published: 2026-07-16
Source: https://osv.dev/vulnerability/CVE-2026-61718
Type: osv

## Details
bunkerweb is an Open-source and next-generation Web Application Firewall (WAF). From 1.6.2 until 1.6.12, the BunkerWeb web UI BiscuitMiddleware authorization bypass list included the /cache/ URL prefix, so routes in src/ui/app/routes/cache.py protected only by @login_required, including POST /cache/delete, allowed low-privilege read-only reader accounts to permanently delete job cache files containing blacklist, greylist, DNSBL, CrowdSec, GeoIP, ModSecurity CRS, Let's Encrypt, ACME, and custom configuration data. This issue is fixed in version 1.6.12.

## References
- https://github.com/bunkerity/bunkerweb/releases/tag/v1.6.12
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/61xxx/CVE-2026-61718.json
- https://github.com/bunkerity/bunkerweb/security/advisories/GHSA-q7rm-935c-v39g
- https://nvd.nist.gov/vuln/detail/CVE-2026-61718
- https://github.com/bunkerity/bunkerweb/commit/685ccbbe7d204132a843a7b7fd802d1bdb3f20a9
