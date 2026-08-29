# [H] CVE-2026-34377: Consensus Failure via Crafted V5 Authorization Data

## Summary
Severity: High
Chain: Zcash
Component: ZcashFoundation/zebra
CVE: CVE-2026-34377
CWE: Improper Verification of Cryptographic Signature
Published: 2026-03-27
Source: https://github.com/ZcashFoundation/zebra/security/advisories/GHSA-3vmh-33xr-9cqh
Type: github-advisory

## Details
---

# CVE-2026-34377: Consensus Failure via Crafted V5 Authorization Data

## Summary
A logic error in Zebra's transaction verification cache could allow a malicious miner to induce a consensus split. By matching a valid transaction's `txid` while providing invalid authorization data, a miner could cause vulnerable Zebra nodes to accept an invalid block, leading to a consensus split from the rest of the Zcash network.  To be clear, **this would not allow invalid transactions to be accepted** but could result in a consensus split between vulnerable Zebra nodes and invulnerable Zebra and Zcashd nodes.

## Severity
**High** - This is a Consensus Vulnerability that could allow a malicious miner to induce network partitioning, service disruption, and potential double-spend attacks against affected nodes.

## Affected Versions
All Zebra versions supporting V5 transactions (Network Upgrade 5 and later) prior to **version 4.3.0**.

## Description
The vulnerability exists in the `find_verified_unmined_tx` function within `transaction.rs`. This function was designed to optimize block verification by checking if a transaction was already verified in the mempool.

The lookup mechanism used the **ZIP-244 `txid`** as the unique key. However, for V5 transactions, the `txid` specifically excludes the **Authorization Data Root** (signatures and proofs). Because Zebra returned a "verified" status based solely on the `txid`, it skipped the essential `check_v5_auth()` call for the transaction version provided in the block.

An attacker (specifically a malicious miner) could exploit this by:
1. Observing a valid V5 transaction broadcast to the network and entering a Zebra node's mempool.
2. Creating a block containing a modified version of that transaction. The modified version has the same `txid` but contains invalid signatures or proofs.
3. The affected Zebra node identifies the `txid` in its mempool and incorrectly assumes the block's version of the transaction is already verified.
4. The node commits the block with the invalid transaction data.
5. Other nodes (like `zcashd` or `zebra` nodes without that transaction in their mempool) reject the block, resulting in a chain fork where the poisoned Zebra node is isolated.

## Impact
**Consensus Failure**
* **Attack Vector:** Network (specifically via a malicious miner).
* **Effect:** Network partition/consensus split.
* **Scope:** Any Zebra node utilizing the transaction verification cache optimization for V5 transactions.

## Fixed Versions
This issue is fixed in **Zebra 4.3.0**. 

The fix ensures that verification is only skipped if the transaction's full integrity—including authorization data—is validated against the mempool entry.

## Mitigation
Users should upgrade to **Zebra 4.3.0** or later immediately. 

_Trimmed to 38 lines — full report: https://github.com/ZcashFoundation/zebra/security/advisories/GHSA-3vmh-33xr-9cqh_
