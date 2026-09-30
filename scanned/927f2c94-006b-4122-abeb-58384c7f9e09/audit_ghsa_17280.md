# [C] ZITADEL Vulnerable to Unauthenticated Full-Read SSRF via V2 Login

## Summary
Severity: Critical
Advisory: GHSA-7wfc-4796-gmg5
CVE: CVE-2025-67494
CWE: CWE-918
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2025-12-08
Source: https://github.com/advisories/GHSA-7wfc-4796-gmg5
Type: github-advisory

## Affected
- Go: `github.com/zitadel/zitadel` — affected >=0 <1.80.0-v2.20.0.20251208091519-4c879b47334e
- Go: `github.com/zitadel/zitadel` — affected >=1.83.4
- Go: `github.com/zitadel/zitadel` — affected >=4.0.0-rc.1 <4.7.1
- Go: `github.com/zitadel/zitadel/v2` — affected >=0 <1.80.0-v2.20.0.20251208091519-4c879b47334e

## Details
### Summary

Zitadel is vulnerable to an unauthenticated, full-read SSRF vulnerability. An unauthenticated remote attacker can force Zitadel into making HTTP requests to arbitrary domains, including internal addresses. The server then returns the upstream response to the attacker, enabling data exfiltration from internal services.

### Impact

ZITADEL Login UI (V2) was vulnerable to service URL manipulation through the x-zitadel-forward-host header. The service URL resolution logic treated the header as a trusted fallback for all deployments, including self-hosted instances. This allowed unauthenticated attacker to force the server to make outbound requests and read the responses, reaching internal services, exfiltrating data, and bypassing IP-based or network-segmentation controls. 
 
### Affected Versions

Systems using the login UI (v2) and running one of the following versions are affected:
- **v4.x**: `4.0.0-rc.1` through `4.7.0`

### Patches

The vulnerability has been addressed in the latest release. The patch resolves the issue by correctly validating the x-zitadel-forward-host, resp. all forwarded headers against the instance domains and trusted domains. It's no longer used to route traffic to the Zitadel API.

Before you upgrade, ensure that:
- the `ZITADEL_API_URL` is set and is pointing to your instance, resp. system in multi-instance deployments.
- the HTTP `host` (or a `x-forwarded-host`) is passed in your reverse proxy to the login UI.
- a `x-zitadel-instance-host` (or `x-zitadel-forward-host`) is set in your reverse for multi-instance deployments. If you're running a single instance solution, you don't need to take any actions.

Fixed versions:
- 4.x: Upgrade to >=[4.7.1](https://github.com/zitadel/zitadel/releases/tag/v4.7.1)

### Workarounds

The recommended solution is to update ZITADEL to a patched version.

A ZITADEL fronting proxy can be configured to delete all `x-zitadel-forward-host` header values or set it to the requested host before sending requests to ZITADEL self-hosted environments.

### Questions

If you have any questions or comments about this advisory, please email us at [security@zitadel.com](mailto:security@zitadel.com)

### Credits

Thanks to Amit Laish – GE Vernova for finding and reporting the vulnerability.

## References
- https://github.com/zitadel/zitadel/security/advisories/GHSA-7wfc-4796-gmg5
- https://nvd.nist.gov/vuln/detail/CVE-2025-67494
- https://github.com/zitadel/zitadel/commit/4c879b47334e01d4fcab921ac1b44eda39acdb96
- https://github.com/zitadel/zitadel
