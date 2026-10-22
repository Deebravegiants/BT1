# [M] M-05 | ERC-777 Reentrancy In reinvest

## Summary
Severity: Medium
Contest weight: 0.1080
Dataset id: 2133
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When the bounty is sent to the given bountyTo address with an ERC-777 token the receiver can re-enter the system. At this point, the fee growth values of the position were already reset, but the position had not received the liquidity yet. Therefore the collateral value of the position is smaller than it is in reality. This could lead to the system seeing the position as liquidatable or underwater when the caller reenters the system. Therefore a malicious actor can potentially abuse this state to either: • Liquidate the position to steal from its owner • Call restructureBadDebt to reduce the debt of the position and steal from the lenders (could be abused by the owner of the position)

## Recommendation
Transfer the bounty to the given bountyTo address after all state changes occurred.
