# [M] Reddio incident: Reddio’s RedSonic Vault on Ethereum was exploited for about 9.25 ETH (~$22,800). After permissionlessly registering an stETH vault

## Summary
Severity: Medium
Target: Reddio
Loss: $ 22,800
Attack method: Smart Contract Vulnerability
Published: 2026-09-05
Source: https://x.com/SlowMist_Team/status/2096439593403089077
Type: slowmist-incident

## Details
Reddio’s RedSonic Vault on Ethereum was exploited for about 9.25 ETH (~$22,800). After permissionlessly registering an stETH vault, the same stETH was counted in both the ETH vault and the stETH vault. The attacker used a flash loan to inflate the rsvETH share price, redeemed excess ETH, then redeemed rsvstETH to recover the same stETH.
