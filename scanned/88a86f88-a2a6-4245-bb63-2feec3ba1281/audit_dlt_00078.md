# [H] Cached Mempool Verification Bypasses Consensus Rules for Ahead-of-Tip Blocks

## Summary
Severity: High
Chain: Zcash
Component: ZcashFoundation/zebra
CVE: CVE-2026-40880
Published: 2026-04-17
Source: https://github.com/ZcashFoundation/zebra/security/advisories/GHSA-xvj8-ph7x-65gf
Type: github-advisory

## Details
# CVE-2026-40880: Cached Mempool Verification Bypasses Consensus Rules for Ahead-of-Tip Blocks

## Summary

A logic error in Zebra's transaction verification cache could allow a malicious miner to induce a consensus split. By carefully submitting a transaction that is valid for height `H+1` but invalid for `H+2` and then mining that transaction in a block at height `H+2`, a miner could cause vulnerable Zebra nodes to accept an invalid block, leading to a consensus split from the rest of the Zcash network.

## Severity

High - This is a Consensus Vulnerability that could allow a malicious miner to induce network partitioning, service disruption, and potential double-spend attacks against affected nodes.

## Affected Versions

All Zebra versions prior to version 4.3.1. (Some older versions are not affected but are no longer supported by the network)

## Description

The vulnerability exists due to a performance optimization whose goal is to improve performance of transaction validation if the transaction was previously accepted into the mempool (and thus was verified as valid). That however did not take into account that a transaction can be valid for a specific height, but invalid at higher heights; for example, it can contain an expiry height, a lock time, and it is always bound to a network upgrade, all of which are height-dependant.

An attacker (specifically a malicious miner) could exploit this by (e.g. in the expiry height case):

- Submitting a transaction with expiry height `H+1` (where `H` is the height of the current tip)
- Mining a block `H+1`, and a block `H+2` that contains that same transaction, and submitting block `H+2` before `H+1`
- Zebra nodes would accept `H+2` as valid (pending contextual verification) and wait for block `H+1`; when it arrives, Zebra would commit both blocks even if `H+2` contains an expired transaction
- Other nodes (like `zcashd` or `zebrad` nodes without that transaction in their mempool) reject the block, resulting in a chain fork where the poisoned Zebra node is isolated.

## Impact

**Consensus Failure**

**Attack Vector**: Network (specifically via a malicious miner).
**Effect**: Network partition/consensus split.
**Scope**: Any Zebra node utilizing the transaction verification cache optimization for V5 transactions.

## Fixed Versions

This issue is fixed in **Zebra 4.3.1**.

We removed the performance optimization altogether, since we deemed it too risky.

_Trimmed to 38 lines — full report: https://github.com/ZcashFoundation/zebra/security/advisories/GHSA-xvj8-ph7x-65gf_
