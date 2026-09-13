# [C] cheqd-node Security patch for upstream vulnerabilities in IBC-Go (ISA-2025-001) and Cosmos SDK (ISA-2025-002)

## Summary
Severity: Critical
Advisory: GHSA-h2rp-8vpx-q9r4
CWE: CWE-1395
Ecosystem: Go
Published: 2025-03-13
Source: https://github.com/advisories/GHSA-h2rp-8vpx-q9r4
Type: github-advisory

## Affected
- Go: `github.com/cheqd/cheqd-node` — affected >=0 <3.1.8

## Details
# Description

There have been two upstream security advisories and associated patches published under [ISA-2025-001](https://github.com/cosmos/ibc-go/security/advisories/GHSA-4wf3-5qj9-368v) and [ISA-2025-002](https://github.com/cosmos/cosmos-sdk/security/advisories/GHSA-47ww-ff84-4jrg).

**[ISA-2025-001](https://github.com/cosmos/ibc-go/security/advisories/GHSA-4wf3-5qj9-368v)** affects the IBC-Go package., where non-deterministic JSON unmarshalling of IBC Acknowledgements can result in a chain halt. 

**[ISA-2025-002](https://github.com/cosmos/cosmos-sdk/security/advisories/GHSA-47ww-ff84-4jrg)** affects the Cosmos SDK package, where `x/group` can halt when erroring in `EndBlocker`.

### Impact
If unaddressed, this could result in a chain halt.

### Patches
Validators, full nodes, and IBC relayers should upgrade to [cheqd-node v3.1.8](https://github.com/cheqd/cheqd-node/releases/tag/v3.1.8). This upgrade does not require a software upgrade proposal on-chain and is meant to be non state-breaking.

## References
- https://github.com/cheqd/cheqd-node/security/advisories/GHSA-h2rp-8vpx-q9r4
- https://github.com/cosmos/cosmos-sdk/security/advisories/GHSA-47ww-ff84-4jrg
- https://github.com/cosmos/ibc-go/security/advisories/GHSA-4wf3-5qj9-368v
- https://github.com/cheqd/cheqd-node/commit/5a58b08dfb8dfc24631fb85b641cb75e9178d07f
- https://github.com/cheqd/cheqd-node
- https://github.com/cheqd/cheqd-node/releases/tag/v3.1.8
