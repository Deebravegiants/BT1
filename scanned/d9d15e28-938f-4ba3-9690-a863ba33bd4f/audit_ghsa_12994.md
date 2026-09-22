# [M] Cloudflare Wrangler directory traversal vulnerability

## Summary
Severity: Medium
Advisory: GHSA-8c93-4hch-xgxp
CVE: CVE-2023-3348
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:A/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-08-03
Source: https://github.com/advisories/GHSA-8c93-4hch-xgxp
Type: github-advisory

## Affected
- npm: `wrangler` — affected >=0 <2.20.1

## Details
### Impact 
The Wrangler command line tool (<=wrangler@3.1.0 or <=wrangler@2.20.1) was affected by a directory traversal vulnerability when running a local development server for Pages (wrangler pages dev command). This vulnerability enabled an attacker in the same network as the victim to connect to the local development server and access the victim's files present outside of the directory for the development server.

### Patches
Wrangler2: Upgrade to v2.20.1 or higher.
Wrangler3: Upgrade to v3.1.1 or higher.

### References
[Workers SDK on Github](https://github.com/cloudflare/workers-sdk)
[Wrangler docs](https://developers.cloudflare.com/workers/wrangler/)
[CVE-2023-3348](https://www.cve.org/CVERecord?id=CVE-2023-3348)

## References
- https://github.com/cloudflare/workers-sdk/security/advisories/GHSA-8c93-4hch-xgxp
- https://nvd.nist.gov/vuln/detail/CVE-2023-3348
- https://github.com/cloudflare/workers-sdk/pull/3498
- https://github.com/cloudflare/workers-sdk/commit/fddffdf0c23d2ca56f2139a2c6bc278052594cba
- https://developers.cloudflare.com/workers/wrangler
- https://github.com/cloudflare/workers-sdk
- https://github.com/cloudflare/workers-sdk/releases/tag/wrangler%403.1.1
