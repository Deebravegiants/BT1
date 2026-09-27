# [H] Pangolin < 1.22.0 Authentication Bypass via Share-Link Endpoint

## Summary
Severity: High
Advisory: CVE-2026-72001
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-31
Source: https://osv.dev/vulnerability/CVE-2026-72001
Type: osv

## Details
Pangolin before 1.22.0 contains an authentication bypass vulnerability that allows unauthenticated attackers to access any protected resource by supplying an attacker-controlled URL parameter to the share-link authentication endpoint that omits the expected resource identifier from the token verification call. Attackers holding a single valid share link for any resource can authenticate against arbitrary resources across different organizations, bypassing all configured authentication methods including SSO, resource passwords, PIN codes, email allowlists, and header authentication.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72001.json
- https://github.com/fosrl/pangolin/releases/tag/1.22.0
- https://nvd.nist.gov/vuln/detail/CVE-2026-72001
- https://www.vulncheck.com/advisories/pangolin-authentication-bypass-via-share-link-endpoint
- https://github.com/fosrl/pangolin
