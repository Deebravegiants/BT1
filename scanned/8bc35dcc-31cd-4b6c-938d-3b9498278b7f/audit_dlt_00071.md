# [M] Allocation Amplification in Inbound Network Deserializers

## Summary
Severity: Medium
Chain: Zcash
Component: ZcashFoundation/zebra
CVE: CVE-2026-44500
CWE: Allocation of Resources Without Limits or Throttling
Published: 2026-05-02
Source: https://github.com/ZcashFoundation/zebra/security/advisories/GHSA-438q-jx8f-cccv
Type: github-advisory

## Details
# CVE-XXXX-XXXXX: Allocation Amplification in Inbound Network Deserializers

## Summary

Several inbound deserialization paths in Zebra allocated buffers sized against generic transport or block-size ceilings before the tighter protocol or consensus limits were enforced. An unauthenticated or post-handshake peer could therefore force the node to preallocate and parse for orders of magnitude more data than the protocol intended, across `headers` messages, equihash solutions in block headers, Sapling spend vectors in V5/V4 transactions, and coinbase script bytes in blocks.

## Severity

**Moderate** - This is a Denial-of-Service Vulnerability that could allow a malicious peer to amplify per-message memory and parse cost on Zebra nodes, with effects amplified by multi-peer fan-in.

Each individual case is bounded by the 2 MiB transport ceiling or the block-size cap, so no single message causes unbounded allocation, but the cumulative gap between intended and actual limits is significant.

## Affected Versions

All Zebra versions prior to 4.4.0

## Description

Zebra's network codec uses `TrustedPreallocate` and generic `Vec` deserialization to bound inbound message parsing. In several places the bound used at the deserializer was the generic transport or block-size ceiling rather than the tighter protocol or consensus rule that applies to the field, so allocation happened first and the real limit was only enforced afterwards. Four such cases were identified:

- **`headers` message receive cap.** `read_headers()` deserialized the `CountedHeader` vector via the generic `TrustedPreallocate` path, which allowed up to ~1,409 entries per message. The protocol ceiling `MAX_FIND_BLOCK_HEADERS_RESULTS = 160` was only used on the send side, giving an ~8.8x preallocation gap on receive. Reachable before the version handshake completes since the codec is installed on raw bytes.
- **Equihash solution length.** `Solution::zcash_deserialize` decoded the solution as a generic `Vec<u8>` and only checked the exact consensus size (1344 bytes mainnet/testnet, 36 bytes regtest) afterwards in `Solution::from_bytes`. A single fixed-size header field could be inflated to nearly the full block-size ceiling before rejection.
- **Sapling spend vectors in coinbase transactions.** V5 `spend_prefixes` and V4 `shielded_spends` were allocated generically with block-size-derived ceilings (~5,681 / ~5,208 entries) before the consensus rule that coinbase transactions have zero Sapling spends was enforced in the verifier.
- **Coinbase script bytes.** `Input::zcash_deserialize()` read the coinbase script as a generic `Vec<u8>` up to the message-size cap before enforcing the consensus rule that coinbase scripts are between 2 and 100 bytes.

An attacker could exploit this by:

- Opening an inbound TCP connection (and, for the latter three cases, completing the version handshake).
- Sending one of: a `headers` message with a CompactSize count up to ~1,409, a `block` whose header carries an inflated equihash CompactSize, a `tx` declaring a coinbase input with a large `nSpendsSapling`, or a `block` with a coinbase input whose script length is near the message-size ceiling.
- The deserializer allocates against the loose ceiling, parses, and only then rejects.

## Impact

**Denial of Service**

- **Attack Vector:** Network.
- **Effect:** Amplified per-message allocation and parse cost on inbound peer messages, stackable across concurrent connections. The concrete effect will be influenced by how much memory Zebra has available.
- **Scope:** Any affected Zebra node.

_Trimmed to 38 lines — full report: https://github.com/ZcashFoundation/zebra/security/advisories/GHSA-438q-jx8f-cccv_
