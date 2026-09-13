# [M] Refund does not restore the cap

## Summary
Severity: Medium
Source: https://github.com/pods-finance/yield-contracts/blob/9389ab46e9ecdd1ea1fd7228c9d9c6821c00f057/contracts/vaults/BaseVault.sol#L412
Type: audit-issue

## Details
When a user deposits into the vault by joining the deposit queue, the corresponding shares, yet to be minted, are [deducted from the spending cap](https://github.com/pods-finance/yield-contracts/blob/9389ab46e9ecdd1ea1fd7228c9d9c6821c00f057/contracts/vaults/BaseVault.sol#L412) immediately. The spending cap is [restored](https://github.com/pods-finance/yield-contracts/blob/9389ab46e9ecdd1ea1fd7228c9d9c6821c00f057/contracts/vaults/BaseVault.sol#L436) only at withdrawal when the shares are burned.

If one user decides to use the [refund](https://github.com/pods-finance/yield-contracts/blob/9389ab46e9ecdd1ea1fd7228c9d9c6821c00f057/contracts/vaults/BaseVault.sol#L333) function to leave the queue before the round ends, the spending cap will not be restored. When the [cap is not zero](https://github.com/pods-finance/yield-contracts/blob/9389ab46e9ecdd1ea1fd7228c9d9c6821c00f057/contracts/mixins/Capped.sol#L22), a malicious user with a sufficiently large amount of assets could repeatedly deposit and `refund` to reach the cap limit and stop other eligible users from joining the queue.

Note that the [spendCap](https://github.com/pods-finance/yield-contracts/blob/9389ab46e9ecdd1ea1fd7228c9d9c6821c00f057/contracts/mixins/Capped.sol#L9) variable cannot be manually restored, but the owner can [reset](https://github.com/pods-finance/yield-contracts/blob/9389ab46e9ecdd1ea1fd7228c9d9c6821c00f057/contracts/configuration/ConfigurationManager.sol#L55) the cap to a higher value to unlock the deposit.

Consider accounting for the available cap during refunds from the queue.

**Update:** _Fixed in commit [4a2e475](https://github.com/pods-finance/yield-contracts/pull/43/commits/4a2e475fb1242cf3306291afff53be55b8c214d0)._
