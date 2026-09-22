# [M] LP rewards in `liquidity_lockbox` can be arbitraged

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-12-autonolas
Published: 2024-01-08
Source: https://github.com/code-423n4/2023-12-autonolas-findings/issues/444
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2023-12-autonolas/blob/main/lockbox-solana/solidity/liquidity_lockbox.sol#L295-L307


# Vulnerability details

## Impact
The [`liquidity_lockbox`](https://github.com/code-423n4/2023-12-autonolas/blob/main/lockbox-solana/solidity/liquidity_lockbox.sol) contract is designed to handle liquidity positions in a specific Orca LP pool. Users can deposit their LP NFTs into the contract, receiving in exchange tokens according to their position size. These tokens are minted with the goal of allowing users to bridge them to Ethereum later on and exchange them for OLAS at a discount.

However, a potential vulnerability arises from the unrestricted nature of the deposit and withdrawal functions. Specifically, a user can deposit a large amount of assets and immediately withdraw all existing positions using the tokens they just received. This sequence of actions can be repeated to continuously exploit the LP rewards system, leading to an unfair distribution of rewards.

The root cause of this issue lies in the `withdraw()` function, which does not have any restrictions or checks that prevent immediate withdrawal after a deposit and pays all accrued LP rewards [to the caller](https://github.com/code-423n4/2023-12-autonolas/blob/main/lockbox-solana/solidity/liquidity_lockbox.sol#L295-L307).

## Proof of Concept
Consider the following scenario:

1. Alice obtains a large amount of tokens either through a [flashloan](https://github.com/solendprotocol/solana-program-library/blob/master/token-lending/program/src/processor.rs#L102) or by buying them.
2. Alice uses these tokens to open a large position in the Orca pool.
3. Alice deposits the position NFT into the `liquidity_lockbox` contract, receiving a large amount of bridge tokens.
4. Alice withdraws all existing positions using the tokens she just received and receives the LP rewards.
5. Alice closes the received positions in the Orca pool, repays the flashloan (if used) and pockets the rewards.

This sequence of actions can be repeated by Alice to continuously exploit the LP rewards system.

## Tools Used
Manual review

## Recommended Mitigation Steps
To mitigate this issue, a possible solution could be to implement a lock-up period for deposited positions. This would prevent users from immediately withdrawing their positions after depositing. Additionally, consider not distributing rewards to the withdrawing user (which will never be fair) and instead collecting them for the protocol.





## Assessed type

Other
