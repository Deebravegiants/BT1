# [M] DoS on withdrawals when the slippage in swaps

## Summary
Severity: Medium
Contest weight: 0.2499
Dataset id: 22919
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When a withdrawal is initiated and the Vault has some loans in Aave, the slippage in swaps to repay the debt can end up being higher than the flash loan repayment, thus reverting the whole withdrawal transaction. When a user initiates a withdrawal, if the Vault has some collateral and debt in Aave, the following steps are going to be followed to process that withdrawal:
1. The Vault is going to request a flash loan from Aave.
2. The Vault will repay the pro-rated debt using the flash loan funds.
3. The Vault will withdraw the pro-rated collateral from Aave.
4. The Vault will swap the withdrawn collateral to WETH.
5. The Vault will swap the WETH to the relevant tokens to repay the flash loan + the flash fees.
When the market is volatile and a user tries to initiate a withdrawal from the Vault, the slippage incurred on those swaps can be higher than the flash loan to repay, thus reverting the whole transaction. Let's look at an example:
1. Vault has 100 USD collateral in LINK and 80 USD debt in OP deposited in Aave (apart from more assets outside Aave).
2. User initiates a withdrawal using half of the total Vault liquidity:
• Vault gets a flash loan of 40 USD in OP and repays the debt.
• Vault withdraws 50 USD in LINK and swaps it all to WETH, incurring 10% in slippage, so the output is 45 USD in WETH.
• Vault swaps 45 USD in WETH to repay the flash loan (40 USD in OP) but the slippage incurred is 13% so there are not enough tokens to get the 40 USD in OP.
3. The whole withdrawal gets reverted because the flash loan cannot be repaid due to the high slippage in swaps.
This issue will halt withdrawals as long as the slippage incurred in the swaps is high. Having on-time withdrawals is critical for the users because when the market is volatile, delayed withdrawals may imply a loss of funds for the users given that Vault share price may be decreasing at a fast rate. Moreover, the manager can trigger this bug by himself to halt withdrawals even if the slippage is null. To do that, a manager can deposit collateral directly in Aave on behalf of the Vault using a non-supported asset by the Vault. When a withdrawal is initiated, the collateral on supported tokens won't be enough to repay the flash loan because the debt to repay is bigger than the accounted collateral. The attack path could be the following:
1. The Vault has 1 WETH as collateral in Aave.
2. The manager deposits directly in Aave 1 rETH on behalf of the Vault.
3. The manager uses the Vault to borrow an amount higher than the accounted collateral, like 5,000 USDC.
4. When the withdrawal is initiated, the flash loan to repay will be 5,000 USD but the collateral withdrawn will only be 1 WETH. Because 1 WETH is less valuable than 5,000 USDC, the flash loan won't be fully repaid, halting the withdrawal.
In step 4, the collateral withdrawn will only be 1 WETH instead of 1 WETH + 1 rETH because the rETH token isn't a token supported by the Vault so it's not available to withdraw from the Vault. DoS on withdrawals when the slippage incurred is high so there are not enough tokens to repay the flash loan on Aave. The manager can also trigger this bug easily to halt withdrawals whenever he desires. This issue breaks a protocol restriction stated in the README:
Depositor under any circumstances should be able to withdraw funds they've invested according to the value of their vault shares given that no lock up is applied. Moreover, given that the manager can trigger this bug without external conditions or requirements, I believe this warrants high severity.

## Recommendation
To mitigate this issue, is recommended that users can initiate a withdrawal specifying which asset to avoid (not withdraw) so that withdrawals are not halted if a single asset cannot be withdrawn.
