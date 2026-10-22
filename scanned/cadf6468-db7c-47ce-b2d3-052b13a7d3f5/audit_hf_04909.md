# [H] Adding liquidity can be DoSed due to calcula-

## Summary
Severity: High
Contest weight: 0.3631
Dataset id: 22827
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When users add liquidity, they send tokens to the ArrakisPublicVaultRouter contract. The ValantisHOTModulePublic contract then takes the required tokens from the ArrakisPublicVaultRouter contract. However, due to a calculation mismatch, the required amount is often greater than the user-sent amount, causing the transaction to be reverted.
Let's consider following scenario:
1. The current state:
• pool: reserve0 = 1e18 + 1, reserve1 = 1e18 + 1
• vault: totalSupply = 1e18 + 1
2. Bob calls the ArrakisPublicVaultRouter.addLiquidity() function with the following parameters:
• amount0Max = 1e18, amount1Max = 1e18
3. At L139, the _getMintAmounts() function returns:
• (sharesReceived, amount0, amount1) = (1e18 - 1, 1e18 - 1, 1e18 - 1)
4. The router contract takes token0 and token1 from Bob in amounts of 1e18 - 1 each and calls the _addLiquidity() function with above parameters.
5. In the _addLiquidity() function, ArrakisMetaVaultPublic.mint(1e18 - 1, Bob) is invoked at L898.
6. In the ArrakisMetaVaultPublic.mint() function:
• at L58, the proportion is recalculated as 1e18 - 1
• _deposit(1e18 - 1) is called at L71
• in the _deposit() function, ValantisHOTModulePublic.deposit(router, 1e18 - 1) is invoked at L150
7. In the ValantisHOTModulePublic.deposit() function:
• amount0 = 1e18, amount1 = 1e18(at L71, L73)
• at L79, L80, it takes token0 and token1 from the router in amounts of 1e18 each
Finally, the process fails because there is only 1e18 - 1 in the router, as mentioned in step 4.
This problem occurs because the calculations in the ArrakisPublicVaultRouter._getMintAmounts() function rely on rounding down. In contrast, the proportion calculation in the ArrakisMetaVaultPublic.mint() function and the amount calculations in the ValantisHOTModulePublic.deposit() function are based on rounding up.
Adding liquidity can be DoSed due to the calculation mismatches.

## Recommendation
The ArrakisPublicVaultRouter._getMintAmounts() function should be updated to return the accurate required amounts.
