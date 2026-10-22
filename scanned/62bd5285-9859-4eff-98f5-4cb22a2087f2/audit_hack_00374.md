# [M] Projekt incident: The Projekt (GREEN/GOLD) reward vault on Ethereum was exploited. The attacker flash-loaned ~14K WETH from Morpho, pushed it into m

## Summary
Severity: Medium
Target: Projekt
Loss: $ 560000
Attack method: Flash Loan Attack
Published: 2026-07-25
Source: https://x.com/DefimonAlerts/status/2081781283584106959
Type: slowmist-incident

## Details
The Projekt (GREEN/GOLD) reward vault on Ethereum was exploited. The attacker flash-loaned ~14K WETH from Morpho, pushed it into multiple Uniswap V2 memecoin pairs and used skim() to create fake “purchase” records. Exploiting the permissionless trackPurchase function (which only reads token balance deltas to size rewards without verifying actual ETH spent), they inflated reward allocations and drained ~301.7 ETH (~$560K) from the vault’s reward pool via massWithdraw.
