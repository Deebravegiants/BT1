# [M] AshAi vectorize change leaks raw embedding-provider errors, including credentials, in a user-facing error

## Summary
Severity: Medium
Advisory: CVE-2026-75760
Aliases: EEF-CVE-2026-75760, GHSA-p5cr-mmmf-6w39
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-31
Source: https://osv.dev/vulnerability/CVE-2026-75760
Type: osv

## Details
Generation of Error Message Containing Sensitive Information vulnerability in ash-project ash_ai discloses provider request state and credentials in a user-facing validation error.

In AshAi.Changes.Vectorize, when the embedding provider call fails the change added a changeset error whose message inspected the raw error term (An error occurred while generating embeddings: #{inspect(error)}). A plain-string add_error produces an Ash.Error.Changes.InvalidChanges in the :invalid class, which AshJsonApi and AshGraphql render back to the caller. The embedding client's error term is not sanitized, so it can carry the request URL, the provider response body, and, for HTTP clients that keep the request in the error struct, the outbound Authorization header with the provider API key. Failures are attacker-reachable via oversized or malformed vectorized content. The fix logs the raw error and returns a generic message.

This issue affects ash_ai: from 0.1.0 before 1.0.0.

## References
- https://cna.erlef.org/cves/CVE-2026-75760.html
- https://github.com
- https://osv.dev/vulnerability/EEF-CVE-2026-75760
- https://repo.hex.pm
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/75xxx/CVE-2026-75760.json
- https://github.com/ash-project/ash_ai/security/advisories/GHSA-p5cr-mmmf-6w39
- https://nvd.nist.gov/vuln/detail/CVE-2026-75760
- https://github.com/ash-project/ash_ai/commit/088a2562e16d65f36cec178070de683636479f58
- https://github.com/ash-project/ash_ai
