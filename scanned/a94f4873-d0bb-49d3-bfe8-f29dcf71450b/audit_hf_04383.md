# [M] M-11 | USDC Claims Will Fail When Using OFT Wrappers

## Summary
Severity: Medium
Contest weight: 0.1243
Dataset id: 21599
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In order to make a batch claimable, admins need to update the totalUsdcInTreasure using dailyUsdcNetFeeRevenue. If the USDC amount added has 6 decimal precision (as most USDC tokens), then the user will receive a 6 decimal amount when the ClaimUsdcRevenueBackward payload is executed.
bool success = IERC20(usdcAddr).transfer(message.receiver, message.tokenAmount);
The protocol plans to allow claims in multiple chains, using both native USDC or OFT wrappers. The issue is that OFT tokens have 18 decimals by default. Therefore, users will receive less tokens than expected when using OFT wrappers (If the protocol launches on BSC, the pegged USDC token has 18 decimals).
Additionally, as the ProxyLedger will transfer native USDC tokens, it should use safeTransfer instead.

## Recommendation
Create the OFT token wrapper for USDC that will be used in the vault chains, overriding decimals to use 6 decimals instead of 18. Ensure that admin updates daily USDC revenue with correct decimals.
