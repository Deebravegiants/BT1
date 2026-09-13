# [M] Incorrect `assetsOf` calculation

## Summary
Severity: Medium
Source: https://github.com/pods-finance/yield-contracts/blob/c4b401ce674c24798de5f9d02c82e466ee0a2600/contracts/vaults/BaseVault.sol#L251
Type: audit-issue

## Details
The [assetsOf](https://github.com/pods-finance/yield-contracts/blob/c4b401ce674c24798de5f9d02c82e466ee0a2600/contracts/vaults/BaseVault.sol#L251) function within `BaseVault` is used to calculate the combination of a user’s idle and withdrawable assets. This should depict the number of underlying assets a user could potentially receive from the vault at any given time. The formula it uses, however, incorrectly sums three separate items:

* The number of assets the user’s entire share balance would currently convert to
* The number of idle assets a user has in the queue
* The number of assets the user’s entire share balance would convert to if the conversion rate factored in all idle assets

During testing, it was observed that the sum of these three items were at least double the amount of assets a user could actually receive from the protocol.

Consider changing the `assetsOf` calculation to match the behavior if a user were to perform both a [redeem](https://github.com/pods-finance/yield-contracts/blob/c4b401ce674c24798de5f9d02c82e466ee0a2600/contracts/vaults/BaseVault.sol#L168) of their total balance of shares and a [refund](https://github.com/pods-finance/yield-contracts/blob/c4b401ce674c24798de5f9d02c82e466ee0a2600/contracts/vaults/BaseVault.sol#L326) of all of their idle assets in the same transaction.

**Update:** _Resolved in [PR#98](https://github.com/pods-finance/yield-contracts/pull/98), with commit `602122efed209eed23f14b5eb906be1fab01cec5` being the last one added._
