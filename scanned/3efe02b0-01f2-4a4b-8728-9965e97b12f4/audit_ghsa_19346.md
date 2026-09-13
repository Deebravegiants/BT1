# [M] Mithril snapshots for Cardano database could be compromised by an adversary

## Summary
Severity: Medium
Advisory: GHSA-qv97-5qr8-2266
CWE: CWE-345
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:N/I:L/A:L (CVSS_V3)
Published: 2025-05-07
Source: https://github.com/advisories/GHSA-qv97-5qr8-2266
Type: github-advisory

## Affected
- crates.io: `mithril-client` — affected >=0 <0.12.2

## Details
### Impact

#### Mithril certification of Cardano database

The Mithril network provides certification for snapshots of the Cardano database, enabling users to quickly bootstrap a Cardano node without relying on the slower peer-to-peer synchronization process.

To generate a multi-signature, a minimum threshold of Cardano stake registered in the protocol must agree on signing the same message. In this context, a digest is computed from the internal files of the Cardano node's database. However, this mechanism has certain limitations. Specifically, some files are not identically generated across all Cardano nodes, and there is no API to provide consistent snapshots at a specific beacon on the Cardano chain:

- All immutable files, except the last one (which is still being created), are used to compute the message
- The last immutable file is excluded from the signature
- The ledger state files are also excluded from the signature.

#### Cardano node startup sequence

A Cardano node can only perform a fast bootstrap if a pre-computed ledger state is loaded into its database; otherwise, a full re-computation is required, which is time-consuming. During the startup phase with a pre-computed ledger state, the node performs structural verification of the ledger state and lightweight conformity checks which may not be enough to systematically detect invalid ledger state.

#### Attack scenarios

Inconsistencies could be introduced into a tampered ledger state distributed through Mithril snapshots, either by an unknown source or by a compromised IOG-operated aggregator. These inconsistencies would not be immediately detected by Cardano nodes started with such snapshots, potentially enabling long-range attacks that might not be corrected by honest nodes, even if they sync from genesis.

Currently, a Mithril network has only one aggregator, which serves snapshots from a secure cloud location operated by IOG and is therefore assumed to be trustworthy. In the future, as Mithril networks become more decentralized, multiple aggregators will operate independently. This increased decentralization could raise the risk of a malicious aggregator distributing a tampered ledger state.

### Patches

As a mitigation, the Mithril aggregator now signs the ledger state snapshot and the latest immutable file using an IOG-owned key, and the client library and CLI validate the signature of these files upon download.

- The **Mithril client library** has been fixed with version `0.12.2`, **previous versions must not be used anymore**.
- The **Mithril client CLI** has been fixed with version `0.12.1`, **previous versions must not be used anymore**.
- The **Mithril aggregator** has been fixed with version `0.7.44`, **previous versions must not be used anymore**.

### References

- _Mithril protocol in depth_: https://mithril.network/doc/next/mithril/mithril-protocol/protocol
- _Bootstrap a Cardano node_: https://mithril.network/doc/manual/getting-started/bootstrap-cardano-node
- _Mithril certification of the Cardano node database_: https://mithril.network/doc/mithril/advanced/mithril-certification/cardano-node-database

## References
- https://github.com/input-output-hk/mithril/security/advisories/GHSA-qv97-5qr8-2266
- https://github.com/input-output-hk/mithril
