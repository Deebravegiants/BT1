# [M] 6.20 Wrong State Variable Updated

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Design Medium Version 8 Code Corrected

The function LStrategy.rebalanceUniV3Vaults updates the wrong state variable when storing the
timestamp of the ongoing rebalance:

```
require(
block.timestamp >= lastRebalanceUniV3VaultsTimestamp + otherParams.secondsBetweenRebalances,
ExceptionsLibrary.TIMESTAMP
);
lastRebalanceERC20UniV3VaultsTimestamp = block.timestamp;
```
Due to this error the throttling mechanism does not work as expected for the function rebalancing the two
uniswap vaults. Furthermore, this also affects the throttling mechanism of the function
rebalanceERC20UniV3Vaults.

Code corrected:

The issue has been fixed and the correct state variable is updated in rebalanceUniV3Vaults:

```
lastRebalanceUniV3VaultsTimestamp = block.timestamp;
```
