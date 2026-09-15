# [M] Rewards will be lost if `LIQUIDITY_MINING_RECEIVER` becomes compromised since there is no way to set it to a new address

## Summary
Severity: Medium
Reporter: rbserver
Source: https://github.com/sherlock-protocol/sherlock-v2-core/blob/355c70df23aa9aa7d46567c9540a6d15be93fcab/contracts/strategy/TrueFiStrategy.sol#L69
Type: audit-issue

## Details
# Rewards will be lost if `LIQUIDITY_MINING_RECEIVER` becomes compromised since there is no way to set it to a new address

## Summary
If `LIQUIDITY_MINING_RECEIVER` becomes compromised, rewards will be lost because `LIQUIDITY_MINING_RECEIVER` cannot be set to a new address.

## Vulnerability Detail
As shown in the Code Snippet section, `LIQUIDITY_MINING_RECEIVER` is hardcoded. As indicated by https://etherscan.io/address/0x666B8EbFbF4D5f0CE56962a25635CfF563F13161#readProxyContract#F9, `LIQUIDITY_MINING_RECEIVER` corresponds to a Gnosis Safe owned by 4 owners. There is no guarantee that this Gnosis Safe will not be compromised in the future in which multiple owners' private keys could be stolen. When this occurs, `LIQUIDITY_MINING_RECEIVER` becomes unsafe for receiving the rewards. However, because `LIQUIDITY_MINING_RECEIVER` is hardcoded, calling the `claimReward` function can only transfer the rewards to `LIQUIDITY_MINING_RECEIVER`, which is already compromised.

## Impact
For the described scenario, the attacker who controls the compromised `LIQUIDITY_MINING_RECEIVER` can call the `claimReward` function to transfer rewards to `LIQUIDITY_MINING_RECEIVER`. As a result, these rewards, which are earned by the `TrueFiStrategy` contract's USDC funds, are all lost.

## Code Snippet
https://github.com/sherlock-protocol/sherlock-v2-core/blob/355c70df23aa9aa7d46567c9540a6d15be93fcab/contracts/strategy/TrueFiStrategy.sol#L69
```solidity
  address public constant LIQUIDITY_MINING_RECEIVER = 0x666B8EbFbF4D5f0CE56962a25635CfF563F13161;
```

https://github.com/sherlock-protocol/sherlock-v2-core/blob/355c70df23aa9aa7d46567c9540a6d15be93fcab/contracts/strategy/TrueFiStrategy.sol#L189-L201
```solidity
  function claimReward() external {
    IERC20[] memory tokens = new IERC20[](1);
    tokens[0] = tfUSDC;

    // Claim TrueFi tokens for tfUSDC
    tfFarm.claim(tokens);

    // How much TrueFi tokens does this contract hold
    uint256 rewardBalance = rewardToken.balanceOf(address(this));

    // Send all TrueFi tokens to LIQUIDITY_MINING_RECEIVER
    if (rewardBalance != 0) rewardToken.safeTransfer(LIQUIDITY_MINING_RECEIVER, rewardBalance);
  }
```

## Tool used

Manual Review

## Recommendation
In the `TrueFiStrategy` contract, `LIQUIDITY_MINING_RECEIVER` can be changed to not be a constant, and an admin function, which is only callable by the users who have the admin-level privilege, can be added for setting `LIQUIDITY_MINING_RECEIVER`.
