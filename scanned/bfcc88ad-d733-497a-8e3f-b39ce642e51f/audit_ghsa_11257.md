# [M] Kargo Vulnerable to SSRF in Promotion http/http-download Steps Enables Internal Network Access and Data Exfiltration

## Summary
Severity: Medium
Advisory: GHSA-j94x-8wcp-x7hm
CVE: CVE-2026-32828
CWE: CWE-918
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:N/VI:N/VA:N/SC:L/SI:N/SA:N (CVSS_V4)
Published: 2026-03-16
Source: https://github.com/advisories/GHSA-j94x-8wcp-x7hm
Type: github-advisory

## Affected
- Go: `github.com/akuity/kargo` — affected >=1.4.0 <1.6.4
- Go: `github.com/akuity/kargo` — affected >=1.7.0-rc.1 <1.7.9
- Go: `github.com/akuity/kargo` — affected >=1.8.0-rc.1 <1.8.12
- Go: `github.com/akuity/kargo` — affected >=1.9.0-rc.1 <1.9.5

## Details
## Summary

Kargo's built-in `http` and `http-download` promotion steps execute outbound HTTP requests from the Kargo controller. By design, these steps do not restrict destination addresses, as there are legitimate use cases for requests to internal and private endpoints. However, this also permits requests to link-local addresses, for which there are no known, legitimate use cases. Of particular concern is the cloud instance metadata endpoint (often `169.254.169.254`), which is unauthenticated and can expose sensitive configuration data including IAM credentials. While cloud providers typically implement header-based SSRF mitigations for these endpoints, the `http` step provides full control over request method and headers, rendering these protections ineffective. The `http-download` step provides control over headers only (not method), but this is still sufficient for exfiltrating data from metadata endpoints.

There are two vectors for exploitation. A user with permission to create or update a Stage can configure its promotion template to include malicious `http` or `http-download` steps. Alternatively, a user with `promote` permission on any Stage can craft a Promotion resource directly. In either case, the controller executes the steps in-cluster, and response data can be inserted into Promotion status fields, written to a Git repository, or sent to a remote location using a second instance of the `http` step.

The remediation for this issue is the introduction of a safe HTTP transport that refuses to dial link-local addresses. Requests to private and internal addresses will continue to be permitted, as this is by design. It is the responsibility of services at such addresses to implement proper authentication and authorization, and/or the responsibility of platform teams to define and enforce network policies that restrict traffic appropriately.

### Base Metrics
 ---
The following sections provide the rationale for the values selected for each of CVSS v4's base metrics.

### Attack Vector (AV): Network
The Kargo API server is accessible over HTTP/HTTPS. No local, adjacent network, or physical access is required.

### Attack Complexity (AC): Low
Exploitation requires only a crafted Promotion manifest submitted via the Kargo API. No race conditions, non-default configurations, or prior information gathering is required.

### Attack Requirements (AT): None
No specific environmental conditions are required beyond a standard Kargo deployment. The http and http-download built-in steps are always available.

### Privileges Required (PR): High
The attacker must be authenticated to the Kargo API server and hold permissions sufficient to create or update a Stage, or to craft a Promotion resource directly. Although these may not be considered administrative permissions, they are non-trivial, not granted broadly by default, and must be explicitly assigned by a project administrator.

### User Interaction (UI): None
The attack is fully automated via API calls. No other user needs to take any action. The controller processes the malicious Promotion without human intervention.

### Confidentiality Impact to Vulnerable System (VC): None
Kargo itself does not expose its own secrets or configuration data through this vulnerability. The impact is to other systems reachable from the controller's network position, not to Kargo's own data.

### Integrity Impact to Vulnerable System (VI): None
Kargo's own data and configuration are not modified by this vulnerability. While malicious Promotion resources are created, they function within Kargo's normal processing pipeline.

### Availability Impact to Vulnerable System (VA): None
This vulnerability does not enable denial of service against Kargo. Each Promotion executes a bounded set of HTTP requests and does not consume disproportionate resources.

### Confidentiality Impact to Subsequent Systems (SC): Low
The controller runs in-cluster and can reach link-local addresses, including cloud instance metadata endpoints. These endpoints are unauthenticated and can expose sensitive data such as IAM credentials. Provider-side header-based SSRF mitigations are ineffective because these steps provide full control over request headers.

### Integrity Impact to Subsequent Systems (SI): None
Cloud instance metadata endpoints are read-only. While the http step supports arbitrary HTTP methods, the only unintended access enabled by this vulnerability is to link-local addresses, and these do not accept state-changing requests.

### Availability Impact to Subsequent Systems (SA): None
A single HTTP request per promotion step does not constitute a meaningful denial-of-service vector against subsequent systems. There is no amplification mechanism.

## Mitigating Factors

- Exploitation requires authentication to the Kargo API server with permissions to create or update Stages, or to craft Promotion resources directly. These permissions must be explicitly granted by a project administrator.

- All Promotion creation is audited. The creating user's identity is recorded in annotations and Kubernetes events, providing a clear forensic trail.

- The practical impact is limited to cloud instance metadata endpoints. Access to private and internal addresses is by design, and services at those addresses are expected to implement their own authentication and authorization.

## References
- https://github.com/akuity/kargo/security/advisories/GHSA-j94x-8wcp-x7hm
- https://nvd.nist.gov/vuln/detail/CVE-2026-32828
- https://github.com/akuity/kargo/commit/fd25620c2473ed19bec4be4d0f181287ef0f0391
- https://github.com/akuity/kargo
