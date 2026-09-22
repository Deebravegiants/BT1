# [M] `reportOracle` can be sandwiched for profit.

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
#### Description
The fact that price update happens in an on-chain transaction gives the searches the ability to see the future price and then act accordingly. 

#### Examples
MEV searcher can find the `reportOracle` transaction in the mem-pool and if the price is about to increase he could proceed to mint as much gETH as he can with a flash loan. They would then bundle the `reportOracle` transaction. Finally, they would redeem all the gETH for ETH at a higher price per share value as the last transaction in the bundle.

This paired with the fact that oracle might be updated less frequently than once per day, could lead to the fact that profits from this attack will outweigh the fees for performing it.

Fortunately, due to the nature of the protocol, the price fluctuations from day to day will most likely be smaller than the fees encountered during this arbitrage, but this is still something to be aware of when updating the values for DWP donations and fees. But it also makes it crucial to update the oracle every day not to increase the profit margins for this attack.
