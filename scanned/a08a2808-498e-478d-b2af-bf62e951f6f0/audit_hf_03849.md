# [M] liquidationTarget is not set when removing

## Summary
Severity: Medium
Contest weight: 0.0000
Dataset id: 20101
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability concerns a missing state update during the liquidity removal process of a decentralized exchange pool. Specifically, when a user invokes the function that removes liquidity, the internal variable that records the address or identifier of the liquidation target is never assigned. This omission means the contract lacks the necessary reference to direct the withdrawn assets to the correct recipient or to trigger the appropriate accounting steps. As a result, the removal transaction may complete without reverting, but the expected transfer of tokens does not occur, leaving the user’s balance unchanged and the pool in an inconsistent state. The root cause is a logical oversight in the removal routine where the liquidationTarget field is not set before the final settlement logic executes. Exploitation is straightforward: any participant attempting to withdraw liquidity will experience a failed or silent removal, effectively locking their funds in the pool. In a worst‑case scenario, an attacker could repeatedly trigger removal attempts to keep the pool in a broken state, preventing other liquidity providers from exiting and potentially causing a loss of confidence in the protocol. The issue manifests only when the removal path is taken; normal trading operations remain unaffected. It primarily affects liquidity providers who expect to receive their proportional share of assets after calling the removal function, as well as the protocol itself, which relies on accurate accounting for solvency and fee distribution. The problem was identified during a manual audit that examined state transitions and noticed that the liquidationTarget variable remained unset after a removal call. Because the contract does not emit a specific error or event for this condition, the bug can be hard to detect through standard testing or transaction monitoring. To remediate the issue, the removal logic should be amended to explicitly assign the correct liquidation target before any asset transfers or accounting updates are performed, and additional checks or events should be added to verify that the target is set, ensuring that withdrawals either succeed fully or revert with a clear error message. This class of bug falls under improper state initialization and can lead to funds disappearing from the user’s perspective, refunds not being issued, and overall accounting breakdown within the pool.

## Recommendation
No recommendation available
