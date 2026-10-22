# [M] DDOS in `BalLiquidityProvider`

## Summary
Severity: Medium
Contest weight: 0.1821
Dataset id: 5413
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability resides in the BalLiquidityProvider contract, where a function that adds liquidity requires the contract's token balance (bal) to be exactly equal to an input parameter _request.maxAmountsIn[i]. This strict equality creates a denial‑of‑service condition because any external actor can alter the contract's balance by sending a trivial amount of the token (for example, 1 wei) before the liquidity‑provider transaction is executed. When the attacker performs this front‑run, the on‑chain balance becomes slightly larger than the value supplied in the request, causing the require statement to fail and the transaction to revert. As a result, legitimate liquidity providers are unable to submit their deposits, the pool does not receive new liquidity, and expected fees or market‑making functions are blocked. The issue surfaces whenever the add‑liquidity function is called and the contract balance is expected to match the caller‑provided maximum amount; it can be triggered repeatedly with negligible cost to the attacker. The parties impacted include liquidity providers who see their transactions revert with a balance mismatch error, the protocol that loses fresh capital and potentially suffers reduced trading volume, and end‑users who may experience higher slippage or missing market depth. The problem was discovered during a formal audit when the reviewer noticed the equality check between an externally mutable balance and an input variable, recognizing that the balance can be altered by anyone. It is difficult to notice because the discrepancy may involve only a single wei, which does not appear in most UI dashboards, and the revert message may be generic. This flaw belongs to the broader class of bugs that rely on exact equality with external state, enabling front‑running or other actors to break invariants. To remediate, the contract should either remove the equality requirement entirely or replace it with a non‑strict check such as bal >= _request.maxAmountsIn[i], and should rely on internal accounting rather than the raw token balance to enforce limits. By doing so, the contract no longer depends on an immutable balance value that can be manipulated, thereby eliminating the DoS vector and restoring the expected behavior where users can provide liquidity without unexpected reverts.

## Proof of Concept
* bal is equal to the contract’s balance of the asset: [BalLiquidityProvider.sol#L56](https://github.com/code-423n4/2022-05-aura/blob/4989a2077546a5394e3650bf3c224669a0f7e690/contracts/BalLiquidityProvider.sol#L56)
  * bal is required to be equal to the input parameter _request.maxAmountsIn[i]: [BalLiquidityProvider.sol#L57](https://github.com/code-423n4/2022-05-aura/blob/4989a2077546a5394e3650bf3c224669a0f7e690/contracts/BalLiquidityProvider.sol#L57)

An attacker can front-run liquidity providers by sending 1 Wei of the asset to make the balance not equal to the input. This can be repeated and be used to impede the liquidity provider from using the function which will always revert since bal != _request.maxAmountsIn[i]

## Recommendation
Balances shouldn’t be required to be equal to an input variable. An attacker can always make the balance a little bigger. This check should be removed or changed to require (bal >= _request.maxAmountsIn[i]).

Fair report 👍 

**[0xMaharishi (Aura Finance) resolved](https://github.com/code-423n4/2022-05-aura-findings/issues/285#issuecomment-1141475216):**

[code-423n4/2022-05-aura#6](https://github.com/code-423n4/2022-05-aura/pull/6)  
[code4rena aurafinance/aura-contracts#84](https://github.com/aurafinance/aura-contracts/pull/84)
