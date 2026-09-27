# [M] TrueFiPool2 pausing will disable Sherlock's strategy allocations

## Summary
Severity: Medium
Reporter: hyh
Source: https://github.com/sherlock-audit/2022-09-sherlock/blob/main/sherlock-v2-core/contracts/strategy/TrueFiStrategy.sol#L85-L104
Type: audit-issue

## Details
# TrueFiPool2 pausing will disable Sherlock's strategy allocations

## Summary

Whenever TrueFiPool2 depositing is paused Sherlock's strategy depositing becomes unavailable as long as TrueFiStrategy has any positive allocation in the strategy graph. As TrueFi isn't the only strategy this means that Sherlock stakers will miss yield from all the other sources due to this.

## Vulnerability Detail

TrueFiPool2 joining can be paused as a part of system emergency handling. Currently in this state Sherlock's strategy allocation call will be reverted with an attempt to join TrueFiPool2 pool that will fail as it's now performed unconditionally. 

## Impact

Sherlock's staking becomes unavailable until TrueFiPool2 unpauses or TrueFiStrategy be manually removed from the graph or have its share reduced to zero. Sherlock maintainer will lose gas costs of the reverted yieldStrategyDeposit() transaction. Current Sherlock stakers will lose the interest from all other strategies for the funds that needed to be allocated for the period of TrueFi pool unavailability.

## Code Snippet

Now TrueFiStrategy's _deposit() always assume that TrueFiPool2 isn't paused, reverting otherwise:

https://github.com/sherlock-audit/2022-09-sherlock/blob/main/sherlock-v2-core/contracts/strategy/TrueFiStrategy.sol#L85-L104

TrueFiPool2 can be paused/unpaused to handle any emergencies:

https://github.com/trusttoken/contracts-pre22/blob/986fefb91fb0619217d17ecf0b4c5b7b921130ed/contracts/truefi2/TrueFiPool2.sol#L465-L469

```solidity
    /**
     * @dev Join the pool by depositing tokens
     * @param amount amount of token to deposit
     */
    function join(uint256 amount) external override joiningNotPaused {
```

https://github.com/trusttoken/contracts-pre22/blob/986fefb91fb0619217d17ecf0b4c5b7b921130ed/contracts/truefi2/TrueFiPool2.sol#L294-L300

```solidity
    /**
     * @dev pool can only be joined when it's unpaused
     */
    modifier joiningNotPaused() {
        require(!pauseStatus, "TrueFiPool: Joining the pool is paused");
        _;
    }
```

https://github.com/trusttoken/contracts-pre22/blob/986fefb91fb0619217d17ecf0b4c5b7b921130ed/contracts/truefi2/TrueFiPool2.sol#L319-L326

```solidity
    /**
     * @dev Allow pausing of deposits in case of emergency
     * @param status New deposit status
     */
    function setPauseStatus(bool status) external override onlyOwner {
        pauseStatus = status;
        emit PauseStatusChanged(status);
    }
```

This can happen periodically and can even take an extended period of time.

Currently Sherlock strategy deposits will be disabled for the whole such period as on reaching the TrueFiStrategy leaf its _deposit() above be reverted:

https://github.com/sherlock-audit/2022-09-sherlock/blob/main/sherlock-v2-core/contracts/Sherlock.sol#L306-L315

## Tool used

Manual Review

## Recommendation

TrueFi strategy is one of the several and having zero interest for its part for the duration of any emergency looks as a more viable approach compared to the full block of Sherlock strategy depositing.

Consider checking the pausing status and just avoiding interaction with the TrueFiPool2 when it's paused, so Sherlock depositing will not be disabled due to that:

https://github.com/trusttoken/contracts-pre22/blob/986fefb91fb0619217d17ecf0b4c5b7b921130ed/contracts/truefi2/TrueFiPool2.sol#L80-L81

```solidity
    // allow pausing of deposits
    bool public pauseStatus;
```

https://github.com/sherlock-audit/2022-09-sherlock/blob/main/sherlock-v2-core/contracts/strategy/TrueFiStrategy.sol#L85-L104

```solidity
  /// @notice Deposit all USDC in this contract in TrueFi
  /// @notice Joining fee may apply, this will lower the balance of the system on deposit
  /// @notice Works under the assumption this contract contains USDC
  function _deposit() internal override whenNotPaused {
+   // Don't try to join when TrueFiPool is paused
+   // This would make the function call revert
+   // https://github.com/trusttoken/contracts-pre22/blob/986fefb91fb0619217d17ecf0b4c5b7b921130ed/contracts/truefi2/TrueFiPool2.sol#L469
+   // Keep USDC for a while instead
+   if (tfUSDC.pauseStatus()) return;
+
    // https://github.com/trusttoken/contracts-pre22/blob/main/contracts/truefi2/TrueFiPool2.sol#L469
    tfUSDC.join(want.balanceOf(address(this)));

    // Don't stake in the tfFarm if shares are 0
    // This would make the function call revert
    // https://github.com/trusttoken/contracts-pre22/blob/main/contracts/truefi2/TrueMultiFarm.sol#L101
    if (tfFarm.getShare(tfUSDC) == 0) return;

    // How much tfUSDC is in this contract
    // Could both be tfUSDC that was already in here before the `_deposit()` call
    // And new tfUSDC that was minted in the `tfUSDC.join()` call
    uint256 tfUsdcBalance = tfUSDC.balanceOf(address(this));

    // Stake all tfUSDC in the tfFarm
    tfFarm.stake(tfUSDC, tfUsdcBalance);
  }
```

These funds will be used with the next yieldStrategyDeposit() call.
