# [M] New rewards cannot be claimed by `TrueFiStrategy` contract if TrueFi upgrades its farming contract with a new reward token

## Summary
Severity: Medium
Reporter: rbserver
Source: https://github.com/sherlock-protocol/sherlock-v2-core/blob/355c70df23aa9aa7d46567c9540a6d15be93fcab/contracts/strategy/TrueFiStrategy.sol#L62-L66
Type: audit-issue

## Details
# New rewards cannot be claimed by `TrueFiStrategy` contract if TrueFi upgrades its farming contract with a new reward token

## Summary
If TrueFi upgrades its farming contract with a new reward token, the `TrueFiStrategy` contract cannot claim any new rewards after the upgrade.

## Vulnerability Detail
As shown in the Code Snippet section, the address of `rewardToken` is hardcoded. Yet, TrueFi's farming contract is behind a proxy that has the address of `0xec6c3FD795D6e6f202825Ddb56E01b3c128b0b10`. If TrueFi starts to use a new farming contract implementation and switches to use a new reward token in which the new implementation could provide a function for updating the reward token that is not a constant or immutable as indicated by https://etherscan.io/address/0x4af280d9e794b5ea6bee039a6f48a6eafd865341#code#F10#L51, then the hardcoded reward token address will not correspond to the new reward token. In this case, calling the `claimReward` function will not transfer any new rewards to `LIQUIDITY_MINING_RECEIVER` since the new reward balance is now recorded by the new reward token, not the old one.

## Impact
Because the `claimReward` function can only transfer the reward balance recorded by the old reward token, `LIQUIDITY_MINING_RECEIVER` cannot receive any new rewards accumulated for the new reward token and, hence, lose these new rewards.

## Code Snippet
https://github.com/sherlock-protocol/sherlock-v2-core/blob/355c70df23aa9aa7d46567c9540a6d15be93fcab/contracts/strategy/TrueFiStrategy.sol#L62-L66
```solidity
  // TrueFi farm, used to stake tfUSDC and earn TrueFi tokens
  ITrueMultiFarm public constant tfFarm =
    ITrueMultiFarm(0xec6c3FD795D6e6f202825Ddb56E01b3c128b0b10);
  // The TrueFi token
  IERC20 public constant rewardToken = IERC20(0x4C19596f5aAfF459fA38B0f7eD92F11AE6543784);
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
In the `TrueFiStrategy` contract, `rewardToken` can be changed to not be a constant, and an admin function, which is only callable by the users who have the admin-level privilege, can be added for setting `rewardToken`.
