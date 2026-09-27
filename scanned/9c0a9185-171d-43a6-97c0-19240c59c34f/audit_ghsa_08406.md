# [M] Fleet: IP spoofing allows bypassing API rate limiting

## Summary
Severity: Medium
Advisory: GHSA-mxmp-wr3w-rvqx
CVE: CVE-2026-46356
CWE: CWE-290
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-14
Source: https://github.com/advisories/GHSA-mxmp-wr3w-rvqx
Type: github-advisory

## Affected
- Go: `github.com/fleetdm/fleet/v4` — affected >=0 <4.80.1

## Details
### Summary
A vulnerability in Fleet's IP extraction logic allows unauthenticated attackers to bypass API rate limiting by spoofing client IP headers. This may allow brute-force login attempts or other abuse against Fleet instances exposed to the public internet.

### Impact
Fleet extracted client IP addresses from request headers (`True-Client-IP`, `X-Real-IP`, `X-Forwarded-For`) without validating that those headers originate from a trusted proxy. The extracted IP is used as the key for rate limiting and IP ban decisions.

As a result, an attacker could rotate the value of these headers on each request, causing Fleet to treat each attempt as coming from a different client. This effectively bypasses per-IP rate limits on sensitive endpoints such as the login API, enabling unrestricted brute-force or credential stuffing attacks.

This issue primarily affects Fleet instances that are directly exposed to the internet without a reverse proxy that overwrites forwarded-IP headers. Instances behind a properly configured proxy or WAF are less affected.

### Workarounds
If an immediate upgrade is not possible, administrators should ensure Fleet is deployed behind a reverse proxy (e.g., nginx, Cloudflare, AWS ALB) that overwrites `X-Forwarded-For` with the true client IP, and apply rate limiting at the proxy or WAF layer.

### For more information
If you have any questions or comments about this advisory:
Email us at [security@fleetdm.com](mailto:security@fleetdm.com)
Join #fleet in [osquery Slack](https://join.slack.com/t/osquery/shared_invite/zt-h29zm0gk-s2DBtGUTW4CFel0f0IjTEw)

### Credits
We thank @fuzzztf for responsibly reporting this issue.

## References
- https://github.com/fleetdm/fleet/security/advisories/GHSA-mxmp-wr3w-rvqx
- https://nvd.nist.gov/vuln/detail/CVE-2026-46356
- https://github.com/fleetdm/fleet
- https://github.com/fleetdm/fleet/releases/tag/fleet-v4.80.1
