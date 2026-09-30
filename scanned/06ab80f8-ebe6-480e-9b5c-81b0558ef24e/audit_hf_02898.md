# [M] CA-1 | Inaccurate Comment

## Summary
Severity: Medium
Contest weight: 0.0280
Dataset id: 16199
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The contract contains a function reportResult that iterates over the entire playersSide mapping to set an isWinner flag for each bettor. This loop is executed on-chain and its gas consumption grows linearly with the number of participants. Because the winner status can be derived directly from the stored result variable, maintaining a separate isWinner mapping and looping through every bettor is unnecessary. The root cause is the design choice to perform an on-chain enumeration of a dynamic mapping, which Solidity does not provide an efficient way to traverse, leading to a gas‑intensive operation. An attacker or any user who triggers reportResult when the participant set is large can cause the transaction to exceed the block gas limit, resulting in a failed transaction and preventing the contract from finalising the betting round. Consequently, legitimate bettors may be unable to claim rewards, and the protocol suffers from increased costs and potential denial‑of‑service. The issue appears only when reportResult is called after a betting round with many bettors; small rounds may not exhibit noticeable gas waste. It affects all participants, the contract owner, and any downstream contracts that rely on the result being recorded. The problem was discovered during a manual audit that examined gas usage patterns and identified an unnecessary for‑loop over a mapping. Because the loop does not produce visible state changes beyond what can be inferred, the inefficiency can be easy to overlook, especially if the contract is not exercised with a large number of bettors. The appropriate fix is to remove the isWinner mapping entirely and compute winner status off‑chain or by a simple comparison with the result variable inside the claim function, thereby eliminating the costly enumeration. This class of bug belongs to the broader category of “unnecessary on‑chain iteration over dynamic data structures” which leads to excessive gas consumption and potential denial‑of‑service. From a user perspective, a transaction that should settle a betting round may revert with an out‑of‑gas error, leaving users with no payout despite having placed a winning bet. The expectation that the contract will automatically mark winners is not met; instead the contract consumes a large amount of gas and may fail, breaking the business logic that winners receive their funds.

## Recommendation
Infer whether or not players are winners based on the result contract variable, don’t maintain the
iswinner mapping.
