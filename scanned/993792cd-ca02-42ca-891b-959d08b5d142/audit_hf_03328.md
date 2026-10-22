# [M] ADLU-1 | Direct Use Of block.number

## Summary
Severity: Medium
Contest weight: 0.0352
Dataset id: 18179
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability stems from the contract using the native EVM variable block.number to record the latest Auto‑Deleveraging (ADL) block instead of the protocol‑specific Chain.currentBlockNumber() (or arbSys.arbBlockNumber()) that returns the correct L1 block identifier on Arbitrum. Because block.number on Arbitrum reflects the L2 block height, it can diverge from the L1 block number that the ADL logic is designed to track. This mismatch means the contract may record an ADL block that is either ahead of or behind the intended reference point. An attacker or a regular user can exploit this timing discrepancy by executing actions in the window where the L2 block has advanced but the L1 reference has not, causing the ADL trigger to be considered not yet reached or already passed. Consequently, positions that should have been liquidated may remain open longer, or conversely, liquidations may be forced prematurely, leading to unexpected loss of funds, zeroed balances, or forced closures that contradict the protocol’s risk parameters. The issue manifests only on L2 environments where the two block counters differ, and it affects any trader, liquidity provider, or other participant relying on correct ADL timing. It was discovered during a manual audit by the Guardian team, who noticed the direct use of block.number where a chain‑aware call was required. The problem is subtle because block.number appears to be a valid block identifier, and typical unit tests on a single‑chain fork may not reveal the discrepancy. To remediate, the contract should replace every occurrence of block.number used for ADL bookkeeping with Chain.currentBlockNumber() (or the equivalent arbSys.arbBlockNumber()) so that the recorded block aligns with the protocol’s intended L1 reference, restoring correct ADL timing and preserving the intended safety guarantees.

## Recommendation
Utilize the Chain.currentBlockNumber() when setting the latest ADL block.
