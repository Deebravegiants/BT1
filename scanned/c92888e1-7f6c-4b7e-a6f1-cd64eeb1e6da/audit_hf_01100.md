# [H] Potential Denial of Service in liquidity migration due to unprotected pair creation

## Summary
Severity: High
Contest weight: 0.1971
Dataset id: 4215
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The addLiquidity() function in both RetardedTokenContract and BeastTokenContract is designed to migrate accumulated funds from the bonding curve to a UniswapV2 pool once the bonding curve phase is complete. The function attempts to create a new trading pair between the token and WETH using createPair(). However, since the pair creation is performed within the migration function itself, a malicious actor could preemptively create the pair, causing the createPair() call inside addLiquidity() to revert. This would effectively block the liquidity migration process, trapping funds in the contract until administrative intervention.

## Recommendation
Move the pair creation logic to the token contract constructor. This ensures the pair is created at deployment time when no external actors can interfere. Since the addLiquidity() function can only be called before tradingActive is set to true, there is no risk of unauthorized liquidity addition before the official migration, a situation that would allow users to steal the liquidity being added by the token contract.
