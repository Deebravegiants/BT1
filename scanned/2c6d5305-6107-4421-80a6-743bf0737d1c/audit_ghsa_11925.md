# [H] OpenClaw has web_search citation redirect SSRF via private-network-allowing policy

## Summary
Severity: High
Advisory: GHSA-g99v-8hwm-g76g
CVE: CVE-2026-31989
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-02
Source: https://github.com/advisories/GHSA-g99v-8hwm-g76g
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.1

## Details
### Summary
Gemini `web_search` citation redirect resolution used a private-network-allowing SSRF policy. A citation URL redirect could target loopback/private/internal destinations and be fetched by the gateway.

### Impact
An attacker who can influence citation redirect targets could trigger internal-network requests from the OpenClaw host.

### Fix
Citation redirect resolution now uses strict/default SSRF policy (no private-network override), blocking localhost/private/internal redirect targets.

### Affected and Patched Versions
- Affected: `<= 2026.2.26`
- Patched: `2026.3.1`

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-g99v-8hwm-g76g
- https://nvd.nist.gov/vuln/detail/CVE-2026-31989
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-server-side-request-forgery-via-web-search-citation-redirect
