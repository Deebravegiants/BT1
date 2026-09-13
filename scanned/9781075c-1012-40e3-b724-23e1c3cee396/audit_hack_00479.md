# [M] LootBot AI incident: LootBot AI’s xLoot NFT Staking contract was exploited via a Logic Error (Duplicate NFT ID in Redemption). The redeem() function di

## Summary
Severity: Medium
Target: LootBot AI
Loss: $ 9,600
Attack method: Smart Contract Vulnerability
Published: 2026-04-15
Source: https://x.com/DefimonAlerts/status/2044709964091187660
Type: slowmist-incident

## Details
LootBot AI’s xLoot NFT Staking contract was exploited via a Logic Error (Duplicate NFT ID in Redemption). The redeem() function did not validate duplicate token IDs in the input array. The _redeemable() logic accumulated ETH rewards per epoch for each ID without checking for duplicates, and the nextRedeem mapping was only updated after payout. The attacker flash-loaned 2.1 ETH, triggered a new epoch, called redeem() with 7 NFT IDs each duplicated 155 times, draining ~6.21 ETH. After repaying the flash loan, net profit was ~4.1 ETH ($9,600). The project appears largely abandoned (last official X activity in 2025).
