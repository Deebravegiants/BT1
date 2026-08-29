# [M] Transaction origin check in ROE Markets make Options positions opened by contract users impossible to reduce or close

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-09-goodentry-mitigation
Published: 2023-09-07
Source: https://github.com/code-423n4/2023-09-goodentry-mitigation-findings/issues/17
Type: code-finding

## Details
# Lines of code

https://github.com/GoodEntry-io/GoodEntryMarkets/blob/2e3d23016fadb45e188716d772cec7c2096fae01/contracts/protocol/lendingpool/LendingPool.sol.0x20#L492
https://github.com/GoodEntry-io/ge/blob/c7c7de57902e11e66c8186d93c5bb511b53a45b8/contracts/PositionManager/OptionsPositionManager.sol#L386
https://github.com/GoodEntry-io/ge/blob/c7c7de57902e11e66c8186d93c5bb511b53a45b8/contracts/PositionManager/OptionsPositionManager.sol#L387
https://github.com/GoodEntry-io/ge/blob/c7c7de57902e11e66c8186d93c5bb511b53a45b8/contracts/PositionManager/OptionsPositionManager.sol#L412


# Vulnerability details

This issue was present in the original contest but I did not notice it as I did not have time to review OptionsPositionManager.

The Roe Markets `LendingPool.sol` that OptionsPositionManager uses is a modified version of Aave V2 with an added `PMTransfer` functionality, that is used by OptionsPositionManager when closing or reducing positions.

This `PMTransfer` only works when the user whose position is being operated on is in soft liquidation, or when the user initiated the transaction themselves:
```Solidity
    if (tx.origin != user) {
      (,,,, uint256 healthFactor) = GenericLogic.calculateUserAccountData(
        user,
        _reserves,
        _usersConfig[user],
        _reservesList,
        _reservesCount,
        _addressesProvider.getPriceOracle()
        );
      require(healthFactor <= softLiquidationThreshold, "Not initiated by user");
```

However, when positions are opened, OptionsPositionManager attributes debt to `user = msg.sender`.

```Solidity
  function buyOptions(
    // ...
  )
    external
  {
    // ...
    LP.flashLoan( address(this), options, amounts, flashtype, msg.sender, params, 0);
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-09-goodentry-mitigation-findings/issues/17_
