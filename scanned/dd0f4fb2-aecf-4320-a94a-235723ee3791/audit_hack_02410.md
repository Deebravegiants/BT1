# [M] Sale can end while being paused

## Summary
Severity: Medium
Source: https://github.com/OpenSTFoundation/SimpleTokenSale/blob/1a1e863441ba0149d7585203f5dbc6e800af00cf/contracts/TokenSale.sol#L215
Type: audit-issue

## Details
The [hasSaleEnded](https://github.com/OpenSTFoundation/SimpleTokenSale/blob/1a1e863441ba0149d7585203f5dbc6e800af00cf/contracts/TokenSale.sol#L215) function can change its return value from false to true during the pause period while there should be an extension of the duration of the token sale. The update of `endTime` is done only after calling the `unpause`function and the state during the pause period may be misreported.

A consequence of this could be losing the ability to update whitelist in [updateWhitelist](https://github.com/OpenSTFoundation/SimpleTokenSale/blob/1a1e863441ba0149d7585203f5dbc6e800af00cf/contracts/TokenSale.sol#L234) function during the pause period.

We recommend updating `hasSaleEnded` function to consider the pause period.

**Update**: _Fixed in [these two commits](https://github.com/OpenSTFoundation/SimpleTokenSale/pull/11/commits)._
