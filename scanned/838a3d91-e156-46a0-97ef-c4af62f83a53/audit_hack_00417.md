# [M] NovaBox incident: The NovaBox platform’s reward pool on Ethereum was hacked. The attacker borrowed 427.5 WETH via an Aave V3 flash loan and exploite

## Summary
Severity: Medium
Target: NovaBox
Loss: $ 93,600
Attack method: Flash Loan Attack
Published: 2026-06-09
Source: https://x.com/f12sec/status/2064610827554922679
Type: slowmist-incident

## Details
The NovaBox platform’s reward pool on Ethereum was hacked. The attacker borrowed 427.5 WETH via an Aave V3 flash loan and exploited a flaw in the reward distribution mechanism (dividends distributed before balance updates on deposits/withdrawals). By first depositing a small amount of NOVA tokens to trigger dividend calculation and then a large ETH deposit to inflate their actual share—while the system still calculated based on the old small share—they generated approximately 145.82 ETH in “phantom dividends,” draining the pool from 65.11 ETH to 0.09 ETH (99.86% loss) in a single transaction. Security firm F12 confirmed it was not a smart contract vulnerability but a flaw in the reward mechanism logic.
