# [M] Fleet has a rate limiting bypass via untrusted client IP headers

## Summary
Severity: Medium
Advisory: GHSA-j8h8-75h3-jg53
CVE: CVE-2026-24000
CWE: CWE-290
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-05-14
Source: https://github.com/advisories/GHSA-j8h8-75h3-jg53
Type: github-advisory

## Affected
- Go: `github.com/fleetdm/fleet/v4` — affected >=0 <4.80.1

## Details
### Impact

Fleet trusted client-supplied IP address headers when determining the source IP for incoming requests. This allowed authenticated and unauthenticated clients to spoof their apparent IP address and bypass per-IP rate limiting controls.

Fleet determines a client’s public IP address using HTTP headers such as:
- X-Forwarded-For
- X-Real-IP
- True-Client-IP

These headers were trusted without validation. An attacker could supply arbitrary values in these headers, causing Fleet to treat each request as originating from a different IP address.

This could allow an attacker to bypass per-IP rate limits and increase the effectiveness of brute-force or password-spraying attempts against authentication endpoints.

This issue does not allow authentication bypass, privilege escalation, data exposure, or remote code execution on its own.

### Workarounds

Run Fleet behind a trusted reverse proxy or load balancer that overwrites client IP headers.

### For more information

If you have any questions or comments about this advisory:

Email us at [security@fleetdm.com](mailto:security@fleetdm.com)
Join #fleet in [osquery Slack](https://join.slack.com/t/osquery/shared_invite/zt-h29zm0gk-s2DBtGUTW4CFel0f0IjTEw)

### Credits

We thank @fuzzztf for responsibly reporting this issue.

## References
- https://github.com/fleetdm/fleet/security/advisories/GHSA-j8h8-75h3-jg53
- https://nvd.nist.gov/vuln/detail/CVE-2026-24000
- https://github.com/fleetdm/fleet
- https://github.com/fleetdm/fleet/releases/tag/fleet-v4.80.1
