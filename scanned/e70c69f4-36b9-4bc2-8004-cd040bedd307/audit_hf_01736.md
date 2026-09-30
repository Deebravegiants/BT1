# [C] CRT-1 Possible underflow

## Summary
Severity: Critical
Contest weight: 0.0518
Dataset id: 9506
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is an arithmetic underflow that can occur in the stake ledger management of the Lido KSM protocol. When a ledger’s total stake is dramatically reduced by a rebalance operation, the recorded stake value becomes very small. If, shortly after this reduction, the ledger is subjected to a large slash – for example because a validator misbehaves – the contract subtracts the slash amount from the already‑low stake without first verifying that the stake is sufficient. Because the subtraction is performed with unchecked arithmetic, the result wraps around to a very large unsigned integer instead of reverting. This underflow corrupts the internal accounting of the affected ledger, causing its recorded balance to appear astronomically high while the actual staked amount is near zero. From a user’s perspective the symptoms may include a sudden loss of expected rewards, a balance that shows zero or an unexpectedly huge number, and the inability to withdraw the correct amount of tokens. The impact is critical: the protocol’s accounting invariants are broken, which can lead to over‑issuance of shares, loss of funds for delegators, and a breach of trust in the staking service. The condition under which the bug manifests is a specific sequence – a rebalance that shrinks a ledger’s stake followed by a slash that exceeds the remaining stake. It affects any delegator whose stake is routed through the impacted ledger, as well as the protocol itself because the total supply of staking tokens may become inconsistent with the recorded ledger totals. The issue was discovered during a formal security audit by MixBytes, which identified the unchecked subtraction in the slash handling code (Lido.sol line 608). The bug is hard to notice because the contract does not revert on underflow, and the resulting large number may only be detected later when aggregate accounting checks fail or when users experience unexpected balance anomalies. To remediate the problem the slash logic should be redesigned so that the penalty is distributed proportionally across all ledgers, ensuring that no single ledger can be forced into a negative balance. Additionally, safe‑math checks or explicit require statements should be added to guarantee that the slash amount never exceeds the ledger’s current stake, thereby preventing the underflow from occurring.

## Recommendation
We recommend distributing slashes across all the ledgers.
