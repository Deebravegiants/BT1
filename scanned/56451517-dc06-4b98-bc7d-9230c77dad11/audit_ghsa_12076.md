# [M] Docker Model Runner OCI Registry Client Vulnerable to Server-Side Request Forgery (SSRF)

## Summary
Severity: Medium
Advisory: GHSA-x2f5-332j-9xwq
CVE: CVE-2026-33990
CWE: CWE-918
Ecosystem: Go
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:L/SI:N/SA:N (CVSS_V4)
Published: 2026-03-30
Source: https://github.com/advisories/GHSA-x2f5-332j-9xwq
Type: github-advisory

## Affected
- Go: `github.com/docker/model-runner` — affected >=0 <1.1.25

## Details
## Summary
Docker Model Runner contains an SSRF vulnerability in its OCI registry token exchange flow. When pulling a model, Model Runner follows the realm URL from the registry's `WWW-Authenticate` header without validating the scheme, hostname, or IP range. A malicious OCI registry can set the realm to an internal URL (e.g., `http://127.0.0.1:3000/`), causing Model Runner running on the host to make arbitrary GET requests to internal services and reflect the full response body back to the caller. Additionally, the token exchange mechanism can relay data from internal services back to the attacker-controlled registry via the `Authorization: Bearer` header.

## Patches
Fixed in Docker Model Runner v1.1.25
Docker Desktop users should update to 4.67.0 or later, which includes the fixed Model Runner.

## Workarounds
For Docker Desktop users, enabling Enhanced Container Isolation (ECI) blocks container access to Model Runner, preventing exploitation. However, if the Docker Model Runner is exposed to localhost over TCP in specific configurations, the vulnerability is still exploitable.

## Impact
An unprivileged container or a malicious OCI registry that the user performed a pull from might issue GET requests to host-local services (localhost, internal network)

## References
- https://github.com/docker/model-runner/security/advisories/GHSA-x2f5-332j-9xwq
- https://nvd.nist.gov/vuln/detail/CVE-2026-33990
- https://github.com/docker/model-runner
