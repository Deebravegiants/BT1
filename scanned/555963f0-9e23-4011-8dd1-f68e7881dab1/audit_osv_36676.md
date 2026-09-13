# [M] TrustTunnel has `client_random_prefix` rule bypass via fragmented or partial TLS ClientHello

## Summary
Severity: Medium
Advisory: CVE-2026-24904
Aliases: GHSA-fqh7-r5gf-3r87
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-01-29
Source: https://osv.dev/vulnerability/CVE-2026-24904
Type: osv

## Details
TrustTunnel is an open-source VPN protocol with a rule bypass issue in versions prior to 0.9.115. In `tls_listener.rs`, `TlsListener::listen()` peeks 1024 bytes and calls `extract_client_random(...)`. If `parse_tls_plaintext` fails (for example, a fragmented/partial ClientHello split across TCP writes), `extract_client_random` returns `None`. In `rules.rs`, `RulesEngine::evaluate` only evaluates `client_random_prefix` when `client_random` is `Some(...)`. As a result, when extraction fails (`client_random == None`), any rule that relies on `client_random_prefix` matching is skipped and evaluation falls through to later rules. As an important semantics note: `client_random_prefix` is a match condition only. It does not mean "block non-matching prefixes" by itself. A rule with `client_random_prefix = ...` triggers its `action` only when the prefix matches (and the field is available to evaluate). Non-matches (or `None`) simply do not match that rule and continue to fall through. The vulnerability is fixed in version 0.9.115.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/24xxx/CVE-2026-24904.json
- https://github.com/TrustTunnel/TrustTunnel/security/advisories/GHSA-fqh7-r5gf-3r87
- https://nvd.nist.gov/vuln/detail/CVE-2026-24904
- https://github.com/TrustTunnel/TrustTunnel/commit/aa5060145506952b9431b0ed3edb52bb6c08d9a6
