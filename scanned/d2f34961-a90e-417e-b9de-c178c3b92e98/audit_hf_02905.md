# [M] SQPR-2 | Arbitrary Prize Distribution

## Summary
Severity: Medium
Contest weight: 0.0192
Dataset id: 16214
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is an unrestricted access control flaw in the prize‑distribution mechanism of the contract. The function that finalises the prize pool, typically called winnersClaimPrizePool, can be invoked by any address once the contract has recorded at least one winner. Because the function lacks a check that the caller is an authorised winner or that the full set of winners has been added, an attacker can trigger the distribution arbitrarily. Exploitation proceeds by monitoring the contract state until a winner is added, then calling winnersClaimPrizePool. The contract will treat the call as a legitimate claim, close the prize pool and execute the payout logic, which may transfer the remaining funds to the caller or to an empty winner list, effectively allowing the attacker to capture the prize pool or to end the pool without proper payouts. The impact is that legitimate participants may receive no reward, their expected balances remain unchanged, and the total prize amount disappears from the contract. This situation occurs under the condition that the contract has entered a state where at least one winner exists but the winner‑addition process is not yet complete. All users of the betting platform, especially the intended winners, are affected because the promised prize may never be delivered. The issue was discovered during a manual audit that flagged the absence of any modifier such as onlyWinner or onlyOwner on the claim function. It can be hard to notice because the UI may simply show a “Claim prize” button without indicating that any address can press it, and the contract may still emit events that look normal. To remediate, the contract should enforce that only addresses that have been explicitly recorded as winners can invoke the claim function, and it should verify that the winner list is finalised before allowing the pool to be closed. In broader terms, this is a classic case of missing access control leading to arbitrary execution of a privileged operation, breaking the accounting assumptions that only authorised parties receive funds and that the prize pool is distributed according to the game rules.

## Recommendation
Make sure to always add all winners at once.
