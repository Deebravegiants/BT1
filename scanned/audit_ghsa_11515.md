# [H] OpenClaw: Browser control startup could continue unauthenticated after auth bootstrap failure

## Summary
Severity: High
Advisory: GHSA-vpj2-69hf-rppw
CVE: CVE-2026-32041
CWE: CWE-306
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2026-03-02
Source: https://github.com/advisories/GHSA-vpj2-69hf-rppw
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.1

## Details
### Summary
When browser control started without explicit auth credentials, OpenClaw attempted to bootstrap auth automatically. In affected versions, if that bootstrap step threw an error, startup could continue and expose browser-control routes without authentication.

### Impact
On affected deployments, a local process (or a loopback-reachable SSRF path) could access browser-control routes, including evaluate-capable actions, without auth.

### Fix
Startup now fails closed: if bootstrap auth fails and no explicit token/password is configured, browser-control startup aborts.

### Affected and Patched Versions
- Affected: `<= 2026.2.26`
- Patched: `2026.3.1`

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-vpj2-69hf-rppw
- https://nvd.nist.gov/vuln/detail/CVE-2026-32041
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-unauthenticated-browser-control-access-via-failed-auth-bootstrap
