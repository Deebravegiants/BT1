# [H] STEA-1 | stETH Price Hardcoded To 1 ETH

## Summary
Severity: High
Contest weight: 0.2426
Dataset id: 20578
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
stETH is a rebasing token. It distributes staking rewards through increasing the balances of users with their accrued APR daily. Since the total supply of stETH represents the total staked ETH plus the staking rewards it has a price that is usually very close to that of ETH. The issue arises due to the price of stETH being hardcoded to 1e18. Even though the token is loosely pegged to ETH, 1 stETH ≠ 1 ETH. 1. When price of stETH < the price of ETH: A. Deposits in stETH will mint more to the user than supposed to, devaluing the shares. B. Withdrawing in stETH will make users receive less than intended, thus losing them funds. 2. When price of stETH > ETH: A. Depositing stETH will output less shares than should, thus damaging the depositor. B. Withdrawing stETH will be more profitable than should be, thus devaluing the shares.

## Proof of Concept
https://github.com/GuardianAudits/RestPoCs/blob/ISU-3/test/Guardian/HardCodedPrice.t.sol

## Recommendation
To mitigate the issue change the stETH adapter's value() function to use the [stETH/ETH Chainlink](https://data.chain.link/ethereum/mainnet/crypto-eth/steth-eth) [Price Feed.](https://data.chain.link/ethereum/mainnet/crypto-eth/steth-eth)
