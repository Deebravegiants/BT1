# [M] Claircore: Unauthenticated attackers can submit manifests with URIs pointing to internal services or cloud metadata endpoints

## Summary
Severity: Medium
Advisory: GHSA-698x-9w2p-7vvp
CVE: CVE-2026-10517
CWE: CWE-918
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:N/A:N (CVSS_V3)
Published: 2026-06-01
Source: https://github.com/advisories/GHSA-698x-9w2p-7vvp
Type: github-advisory

## Affected
- Go: `github.com/quay/claircore` — affected >=0

## Details
A flaw was found in Clair. The fetcher component makes outbound HTTP requests to attacker-supplied URIs from manifest layer descriptors without IP or scheme filtering. When PSK authentication is not configured (opt-in, not enforced by default), an unauthenticated attacker can submit a manifest with a URI pointing to internal services or cloud metadata endpoints. The SSRF is reflective for non-200 responses, leaking up to 256 bytes of error body content via CheckResponse error messages. Operator-managed Red Hat Quay deployments auto-configure PSK and are not exposed to the unauthenticated attack vector.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-10517
- https://access.redhat.com/security/cve/CVE-2026-10517
- https://bugzilla.redhat.com/show_bug.cgi?id=2486779
- https://github.com/quay/claircore
