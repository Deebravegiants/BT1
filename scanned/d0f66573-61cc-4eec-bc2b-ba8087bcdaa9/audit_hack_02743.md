# [M] liquidExit may have an unexpected exit penalty if TrueFi adjusts the penalty or some human error

## Summary
Severity: Medium
Reporter: Chom
Source: https://github.com/sherlock-audit/2022-09-sherlock/blob/main/sherlock-v2-core/contracts/strategy/TrueFiStrategy.sol#L155-L185
Type: audit-issue

## Details
# liquidExit may have an unexpected exit penalty if TrueFi adjusts the penalty or some human error

## Summary
liquidExit may have an unexpected exit penalty if TrueFi adjusts the penalty or some human error

## Vulnerability Detail
```solidity
    // At this point there should be at least `_amount` of tfUSDC in the contract
    // Unstake tfUSDC tokens from the pool, this will send USDC to this contract
    tfUSDC.liquidExit(_amount);
  }
```

liquidExit never checks for exitPenalty. It even allows the operator to liquidExit even if the exit penalty is greater than 10% (in case they changed the rule). The human error which may happen anytime can cause unexpected exit penalty too.

## Impact
Strategy operators may unnoticed the penalty changing or operators may miss calculating the penalty. In this case, sherlock pays more exit penalty than strategy operators calculated. This can be seen as a loss of funds. For example, strategy operators have calculated that we currently get 5% APR from them and their exit penalty is 2% = 3% gain. But they haven't noticed that they have changed the fee by 3x, so the exit penalty is 6%. As a result, we lose 1% instead of gaining 3%.

## Code Snippet

https://github.com/sherlock-audit/2022-09-sherlock/blob/main/sherlock-v2-core/contracts/strategy/TrueFiStrategy.sol#L155-L185

## Tool used

Manual Review

## Recommendation
Add exit penalty safeguard

```solidity
  function liquidExit(uint256 _amount, uint256 _maxExitPenaltyBps) external onlyOwner {
    // https://github.com/trusttoken/contracts-pre22/blob/main/contracts/truefi2/TrueFiPool2.sol#L487
    // here's a spreadsheet that shows the exit penalty at different liquidRatio levels ( = liquidValue / poolValue):
    // https://docs.google.com/spreadsheets/d/1ZXGRxunIwe0eYPu7j4QjCwXxe63tNKtpCvRiJnqK0jo/edit#gid=0

    // Exiting 0 tokens doesn't make sense
    if (_amount == 0) revert ZeroArg();

    // Amount of tfUSDC in this contract
    uint256 tfUsdcBalance = tfUSDC.balanceOf(address(this));
    uint256 tfUsdcStaked = _viewTfUsdcStaked();

    // Exit MAX amount of tokens
    if (_amount == type(uint256).max) {
      _amount = tfUsdcBalance + tfUsdcStaked;
      // Exiting 0 tokens doesn't make sense
      if (_amount == 0) revert InvalidState();
    }
    // We can not withdraw more tfUSDC than we have access to
    else if (_amount > tfUsdcBalance + tfUsdcStaked) revert InvalidArg();

    // Unstake tfUSDC if it isn't in the contract already
    if (_amount > tfUsdcBalance) {
      // Unstake tfUSDC from tfFarm so we are able to exit `_amount`
      tfFarm.unstake(tfUSDC, _amount - tfUsdcBalance);
    }

    uint256 wantBalance = want.balanceOf(address(this));

    // At this point there should be at least `_amount` of tfUSDC in the contract
    // Unstake tfUSDC tokens from the pool, this will send USDC to this contract
    tfUSDC.liquidExit(_amount);

    // Check balance to prevent exit penalty overpaid
    require(want.balanceOf(address(this)) - wantBalance >= _amount * (10000 - _maxExitPenaltyBps) / 10000, "Exit penalty too high");
  }
```
