# [M] Envoy Gateway: Wasm HTTP fetch decompresses gzip without output-size limit

## Summary
Severity: Medium
Advisory: GHSA-cxpq-8v7q-cg56
CVE: CVE-2026-53716
CWE: CWE-789
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-07-16
Source: https://github.com/advisories/GHSA-cxpq-8v7q-cg56
Type: github-advisory

## Affected
- Go: `github.com/envoyproxy/gateway` — affected >=1.8.0-rc.0 <1.8.1
- Go: `github.com/envoyproxy/gateway` — affected >=0 <1.7.4

## Details
Vulnerability report without repro case. Repro case may be added later after harness is complete.

**Preconditions (4):**
- Tenant can create EnvoyExtensionPolicy (baseline)
- Attacker hosts a gzip-bomb at a reachable URL
- sha256 unset (optional field; check is post-decompression anyway)
- No operator Wasm-URL allowlist (none exists in code)

**Description**

getFileFromGZ calls io.ReadAll on a raw gzip.Reader (httpfetcher.go:216) with no output bound, while the compressed input is capped at 256 MiB (httpfetcher.go:139). The bytes originate from a tenant-controlled EnvoyExtensionPolicy.spec.wasm[].code.http.url (envoyextensionpolicy.go:1077 → cache.go:248 → httpfetcher.go:147 → :233), so an untrusted tenant can point at a ~10 MiB gzip-of-zeros and force ~10 GiB allocation in the shared controller process. All candidate guards execute either before the body is buffered or after decompression. OOM-kills, restarts, re-reconciles same CR, crash-loops — persistent cross-tenant control-plane outage with PR:L/AC:L and scope change → HIGH despite availability-only.

## References
- https://github.com/envoyproxy/gateway/security/advisories/GHSA-cxpq-8v7q-cg56
- https://github.com/envoyproxy/gateway
