# [M] TrueFi strategy not withdrawing all fund on strategy upgrade

## Summary
Severity: Medium
Reporter: Chom
Source: https://github.com/sherlock-audit/2022-09-sherlock/blob/main/sherlock-v2-core/contracts/strategy/TrueFiStrategy.sol#L109-L114
Type: audit-issue

## Details
# TrueFi strategy not withdrawing all fund on strategy upgrade

## Summary
TrueFi strategy not withdrawing all fund on strategy upgrade

## Vulnerability Detail
```solidity
  function updateYieldStrategy(IStrategyManager _yieldStrategy) external override onlyOwner {
    if (address(_yieldStrategy) == address(0)) revert ZeroArgument();
    if (yieldStrategy == _yieldStrategy) revert InvalidArgument();

    yieldStrategy.withdrawAll();

    emit YieldStrategyUpdated(yieldStrategy, _yieldStrategy);
    yieldStrategy = _yieldStrategy;
  }
```

updateYieldStrategy call withdrawAll function in yieldStrategy

```solidity
  function _withdrawAll() internal override returns (uint256 amount) {
    // Amount of USDC in the contract
    amount = want.balanceOf(address(this));
    // Transfer USDC to core
    if (amount != 0) want.safeTransfer(core, amount);
  }
```

But in TrueFi, it only withdraw only USDC that has liquidity exited.

## Impact
The fund may not be withdrawn from the original strategy contract before upgrading. The owner may forget that they need to do liquidExit. And it will show that a lot of funds are lost on the front since the fund is still in the old strategy which may not be counted on the frontend.

## Code Snippet

https://github.com/sherlock-audit/2022-09-sherlock/blob/main/sherlock-v2-core/contracts/strategy/TrueFiStrategy.sol#L109-L114

https://github.com/sherlock-audit/2022-09-sherlock/blob/main/sherlock-v2-core/contracts/Sherlock.sol#L272-L280

## Tool used

Manual Review

## Recommendation

Remind owner to do liquidExit first
