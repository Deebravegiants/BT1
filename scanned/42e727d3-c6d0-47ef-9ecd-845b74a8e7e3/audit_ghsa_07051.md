# [H] nebula-mesh: Certificate revocation is never enforced at the mesh

## Summary
Severity: High
Advisory: GHSA-cm26-5974-52h8
CVE: CVE-2026-61699
CWE: CWE-299, CWE-672
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-07-14
Source: https://github.com/advisories/GHSA-cm26-5974-52h8
Type: github-advisory

## Affected
- Go: `github.com/forgekeep/nebula-mesh` — affected >=0 <0.7.1

## Details
### Summary

nebula-mesh revokes a host by adding its certificate fingerprint to a per-CA blocklist and shipping that list to every other agent on each poll. Slack's Nebula enforces certificate revocation ONLY through the `pki.blocklist` list in `config.yml` (no CRL/OCSP). The project's own code states this: `internal/pki/durations.go:15` — "Revocation via the blocklist remains the immediate security control."

The server side is fully implemented (computes per-CA blocklist via `GetBlocklistForCA`, returns it in the agent-updates response, sets `has_updates=true` when non-empty). The agent side was never implemented:

1. The agent decodes the `blocklist` JSON field into `UpdatesResponse.Blocklist` (`internal/agent/poller.go:33`) and then DISCARDS it — `poll()` applies `CertificatePEM`, `CACertPEM`, `ConfigYAML`, but never references `updates.Blocklist` (`internal/agent/poller.go:300-339`).
2. The config generator has NO field to emit `pki.blocklist` — `pkiSection` is only `ca`/`cert`/`key` (`internal/configgen/marshal.go:42-46`) and `GeneratorInput` carries no blocklist (`internal/configgen/generator.go:23-52`). So even the server-rendered `config.yml` shipped via `ConfigYAML` cannot carry it.

Result: a blocked/offboarded/compromised host's certificate is never rejected by its peers. Its handshakes keep succeeding for the full remaining cert lifetime — up to 30 days for agent hosts (`DefaultAgentCertDuration`) and 365 days for mobile hosts (`DefaultMobileCertDuration`). Blocking a host in the UI/API has no effect on the data plane.

### Affected components

- Agent drops the blocklist: `internal/agent/poller.go:33` (decode target), `internal/agent/poller.go:300-339` (poll() applies cert/CA/config, never the blocklist).
- Generator cannot emit it: `internal/configgen/marshal.go:42-46` (`pkiSection{CA,Cert,Key}`), `internal/configgen/generator.go:23-52` (`GeneratorInput` has no blocklist), `internal/api/enroll.go:255-330` (`renderHostConfig`, source of shipped ConfigYAML).
- Server correctly produces/ships it (proves intent): `internal/store/sqlite.go:2034` (`GetBlocklistForCA`), `internal/api/updates.go:182-191` (`resp.Blocklist`), `internal/api/updates.go:277` (`has_updates` set on blocklist change).
- Dead helper: `internal/pki/blocklist.go` (`Blocklist` type) is never used in non-test code — no server-side enforcement either.

### Reachability (hop by hop)

1. Operator clicks Block on host B (or B is compromised/offboarded). B's fingerprint enters the per-CA `blocklist` table.
2. Every other host A under the same CA polls `GET /api/v1/agent/updates`; server returns `blocklist: [<B-fp>, ...]` and `has_updates=true`.
3. A's agent decodes `Blocklist` then discards it; `poll()` has no blocklist branch.
4. Even on a config re-render, `configgen.Generate` emits `pki: {ca,cert,key}` with no `blocklist` key (proven by PoC).
5. A's Nebula daemon has an empty blocklist and accepts handshakes from B's still-valid cert. B keeps full mesh access.

### Impact

Revocation is the only in-band mechanism that isolates a compromised/offboarded host from a Nebula mesh. Because the blocklist never reaches any peer's config.yml, a Blocked host retains full overlay reachability to every peer under its CA (and internal services on the mesh) for up to 30d (agent) / 365d (mobile). An attacker who exfiltrates `host.key`+`host.crt` can run stock slackhq/nebula directly, ignore the agent's 403/410 poll responses, and stay connected after the operator revokes the host. Operator-visible state (UI shows blocked, audit log records it) is misleading.

### Proof of Concept (benign)

`internal/configgen/blocklist_poc_test.go` renders a fully-populated host config and asserts the output contains the `pki` section but NO `blocklist` key:

```
$ go test ./internal/configgen/ -run TestPoC_NMESH001 -v
=== RUN   TestPoC_NMESH001_GeneratedConfigOmitsBlocklist
    CONFIRMED: generated config has a pki section but no blocklist key
    pki:
      ca: /etc/nebula/ca.crt
      cert: /etc/nebula/host.crt
      key: /etc/nebula/host.key
    ...
--- PASS
```

The agent half is verifiable by inspection: `poll()` has branches for CertificatePEM/CACertPEM/ConfigYAML/RekeyRequired but none for Blocklist.

### Distinctness

NOT a duplicate of GHSA-339v / CVE-2026-53602 (revocation durability = a blocked host getting a NEW cert re-issued; its fix `CheckIssuanceAllowed` is present and orthogonal). This bug is that the EXISTING cert is never rejected at peers — the distribution/enforcement layer. Checked against all 17 known advisories; none cover blocklist application in the agent or `pki.blocklist` generation.

### Remediation

1. Add `Blocklist []safeString` to `pkiSection` (yaml `blocklist,omitempty`) and `GeneratorInput`; consider also `pki.disconnect_invalid: true`.
2. Have the agent apply `updates.Blocklist` by re-rendering/rewriting `config.yml` + SIGHUP (same path as `ConfigYAML`). Simplest: fold the blocklist into the server-rendered `ConfigYAML` so it flows through the existing write path.
3. Add a regression test asserting a non-empty server blocklist yields a `pki.blocklist` entry in the agent's written config.yml.

## References
- https://github.com/forgekeep/nebula-mesh/security/advisories/GHSA-cm26-5974-52h8
- https://github.com/forgekeep/nebula-mesh/commit/0426e2f224a9b1e2029029bf923c93ed39d21cdb
- https://github.com/forgekeep/nebula-mesh
- https://github.com/forgekeep/nebula-mesh/releases/tag/v0.7.1
