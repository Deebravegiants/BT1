# [M] Price deviation as is can be circumvented by making smaller trades in a loop

## Summary
Severity: Medium
Contest weight: 0.0370
Dataset id: 10815
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is a price‑deviation bypass that stems from the contract’s reliance on recent price snapshots without verifying that those snapshots originate from earlier blocks. Because the check does not enforce a monotonic block number, an attacker can divide a large intended trade into a series of smaller trades that each appear to respect the allowed deviation when compared only to the immediately preceding snapshot. By executing these micro‑trades sequentially within the same block or across consecutive blocks, the attacker incrementally pushes the reported price upward (or downward), effectively drifting the market price away from the true external reference while staying under the per‑trade deviation threshold. This manipulation can be exploited to obtain a more favorable execution price, causing other users to receive worse rates, lose expected value, or see their balances reduced unexpectedly. The impact is a distortion of the protocol’s pricing logic, leading to potential loss of funds for honest participants, inaccurate accounting, and erosion of trust in the platform’s oracle mechanism. The issue manifests whenever the price‑deviation guard is invoked, which is during any trade that references the stored snapshots; it does not depend on a particular block number but on the absence of a block‑age check. The affected parties include traders, liquidity providers, and any protocol component that relies on the price feed for settlement or liquidation. The flaw was discovered during a manual audit that examined the deviation logic and noticed that the snapshot timestamps were never compared against the current block number, a subtle omission that can easily escape automated testing. Because the price appears to move only in small increments, the problem may not be obvious from a single transaction view, making it hard to detect without systematic stress testing. To remediate, the contract should store the price from the previous block and enforce that any deviation comparison uses a snapshot from an earlier block, or alternatively employ a time‑weighted average price (TWAP) that aggregates over multiple blocks, thereby preventing an attacker from manipulating price by chaining tiny trades within a single block. This change restores the intended invariant that each trade cannot deviate beyond the allowed threshold from a trusted, temporally‑stable reference price, preserving the economic guarantees of the system.

## Recommendation
Store the price of the previous block.
