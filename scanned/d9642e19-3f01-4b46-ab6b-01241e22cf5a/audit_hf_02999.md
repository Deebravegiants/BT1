# [M] TokenShop: purchase function should add _purchasePrices parameter

## Summary
Severity: Medium
Contest weight: 0.1362
Dataset id: 16736
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the purchase function of the TokenShop contract, the price of the NFT is represented by _contractToIdToPrice, and _contractToIdToPrice can be set by the owner in the setContractToIdToPrice function.

If setContractToIdToPrice and the purchase function are executed in the same block, the user may suffer a loss due to the new _contractToIdToPrice.

Consider the following scenarios:

The current _contractToIdToPrice is 500. the user likes the price, and the purchase function is called.

But at this time, the setContractToIdToPrice function is called, setting the _contractToIdToPrice to 1000, and this transaction occurs before executing the purchase function, causing the user to execute the purchase function in the case of _contractToIdToPrice 1000.

## Recommendation
Add the _purchasePrices parameter to the purchase function of TokenShop, and verify that _purchasePrices[i] >= _contractToIdToPrice[_tokenContracts[i]][_ids[i]]

prePO (sponsor) confirmed and resolved:
Fixed in [PR 355](https://github.com/prepo-io/prepo-monorepo/pull/355).

cccz (warden) reviewed mitigation:
Fixed by adding `purchasePrices` parameter in `purchase()` to avoid race condition and ensure that tokens are not purchased at higher prices than the user intended.
