# [M] FoxMarket incident: FoxMarket (a DeFi project on BSC) had its FoxLpBondsPool.stake() function calculate and fix _stakeAmount from a manipulable Pancak

## Summary
Severity: Medium
Target: FoxMarket
Loss: $ 118,700
Attack method: Flash Loan Attack
Published: 2026-08-15
Source: https://x.com/SlowMist_Team/status/2089196291800908164
Type: slowmist-incident

## Details
FoxMarket (a DeFi project on BSC) had its FoxLpBondsPool.stake() function calculate and fix _stakeAmount from a manipulable Pancake AMM spot quote before a large USDT→Fox swap. The attacker used flash loans to skew pair reserves, then addLiquidity used a mismatched ratio; Treasury.lpBonds() trusted the stale value, minted excess Fox tokens, and sent inviter rewards to an attacker-controlled address, which were sold in the same transaction.
