# [H] Valkey has Pre-Authentication DOS from malformed RESP request

## Summary
Severity: High
Advisory: BIT-valkey-2026-27623
Aliases: CVE-2026-27623, GHSA-93p9-5vc7-8wgr
Ecosystem: Bitnami
Published: 2026-02-26
Source: https://osv.dev/vulnerability/BIT-valkey-2026-27623
Type: osv

## Affected
- Bitnami: `valkey` — affected >=9.0.0 <9.0.3

## Details
Valkey is a distributed key-value database. Starting in version 9.0.0 and prior to version 9.0.3, a malicious actor with network access to Valkey can cause the system to abort by triggering an assertion. When processing incoming requests, the Valkey system does not properly reset the networking state after processing an empty request. A malicious actor can then send a request that the server incorrectly identifies as breaking server side invariants, which results in the server shutting down. Version 9.0.3 fixes the issue. As an additional mitigation, properly isolate Valkey deployments so that only trusted users have access.

## References
- https://github.com/valkey-io/valkey/security/advisories/GHSA-93p9-5vc7-8wgr
- https://nvd.nist.gov/vuln/detail/CVE-2026-27623
- https://access.redhat.com/security/cve/CVE-2026-27623
- https://bugzilla.redhat.com/show_bug.cgi?id=2442021
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-27623.json
