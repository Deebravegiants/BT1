# [M] Envoy Gateway: OCI layer extraction allocates make([]byte, h.Size) from untrusted tar header

## Summary
Severity: Medium
Advisory: GHSA-h7pq-86h8-rp5x
CVE: CVE-2026-53717
CWE: CWE-789
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-07-16
Source: https://github.com/advisories/GHSA-h7pq-86h8-rp5x
Type: github-advisory

## Affected
- Go: `github.com/envoyproxy/gateway` — affected >=1.8.0-rc.0 <1.8.1
- Go: `github.com/envoyproxy/gateway` — affected >=0 <1.7.4

## Details
Vulnerability report without repro case. Repro case may be added later after harness is complete.

**Preconditions (4):**
- Tenant can create EnvoyExtensionPolicy (baseline)
- Controller has egress to attacker-controlled OCI registry
- No registry allowlist (none exists in code)
- Layer presents Docker/OCI media type

**Description**

At imagefetcher.go:287, make([]byte, h.Size) uses the attacker-controlled tar-header size; the LimitReader at :278 bounds bytes read from the stream but not the header-declared size returned by tr.Next() (a 512-byte header can claim a multi-TB entry via PAX/GNU encoding). Reached from untrusted tenant input via EnvoyExtensionPolicy spec.wasm[].code.image.url (envoyextensionpolicy.go:1157 → cache.go:262/299 → imagefetcher.go:218 → :287), and the allocation happens for every tar entry regardless of filename. The resulting Go runtime OOM throw is unrecoverable and, because the CRD persists, crash-loops the shared controller — single-request, non-volumetric, cluster-wide DoS.

## References
- https://github.com/envoyproxy/gateway/security/advisories/GHSA-h7pq-86h8-rp5x
- https://github.com/envoyproxy/gateway
