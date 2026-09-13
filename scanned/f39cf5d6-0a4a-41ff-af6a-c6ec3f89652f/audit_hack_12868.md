# [H] Unverified input parameters lead to vulnerability to sandwich attacks

## Summary
Severity: High
Reporter: ontheway
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/MarginDex.vy#L126-L202
Type: audit-issue

## Details
# Unverified input parameters lead to vulnerability to sandwich attacks

## Summary
Attackers can manipulate the **_min_position_amount_out** variable of the **MarginDex.open_trade** function to create a trade with significant slippage. They can then perform a sandwich attack on this trade, causing damage to the protocol funds.

## Vulnerability Detail
Multiple functions are susceptible to sandwich attack risks. Below, we will use **MarginDex.open_trade** as an example.

When there is 1 million USDC available in the pool for lending, the following steps can be taken to execute a sandwich attack that causes damage to the protocol funds:

1. Firstly, utilize a flash loan to borrow a significant amount of USDC and ETH.
2. Next, call the **Vault.fund_account** function to deposit 1 million USDC as collateral.
3. Use a substantial amount of ETH to exchange for USDC, causing the value of USDC in the ETH/USDC trading pool to increase.
4. Call the **MarginDex.open_trade** function and set **_min_position_amount_out** to **0**.
5. Execute the sandwich attack by converting the acquired USDC back to ETH through the ETH/USDC trading pool.
6. Repay the flash loan used in the attack.

## Impact
It will lead to losses in the protocol funds and the loss of principal for users providing liquidity.

## Code Snippet
https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/MarginDex.vy#L126-L202

https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L155-L209

https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/SwapRouter.vy#L60-L98

## Tool used
Manual Review

## Recommendation
It is crucial never to trust user input. Please validate the **_min_position_amount_out** parameter of the **MarginDex.open_trade** function.
Please also check other functions within the protocol that allow users to control the amountOutMinimum parameter, such as **MarginDex.close_trade** and **MarginDex.partial_close_trade**.
I no longer raise new issues regarding this matter.
