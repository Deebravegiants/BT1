# [M] `RTokenAsset` price estimation accounts for margin of error twice

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-07-reserve
Published: 2023-08-04
Source: https://github.com/code-423n4/2023-07-reserve-findings/issues/31
Type: code-finding

## Details
# Lines of code

https://github.com/reserve-protocol/protocol/blob/9ee60f142f9f5c1fe8bc50eef915cf33124a534f/contracts/plugins/assets/RTokenAsset.sol#L53-L72
https://github.com/reserve-protocol/protocol/blob/9ee60f142f9f5c1fe8bc50eef915cf33124a534f/contracts/plugins/assets/RTokenAsset.sol#L100-L115


# Vulnerability details


`RTokenAsset` estimates the price by multiplying the BU (basket unit) price estimation by the estimation of baskets held (then dividing by total supply).
The issue is that both BU and baskets held account for price margin of error, widening the range of the price more than necessary.


## Impact
This would increase the high estimation of the price and decrease the lower estimation.
This would impact:
* Setting a lower min price for trading (possibly selling the asset for less than its value)
* Preventing the sell of the asset (`lotLow` falling below the min trade volume)
* Misestimation of the basket range on the 'parent' RToken

## Proof of Concept


* Both `tryPrice()` and `lotPrice()` use this method of multiplying basket unit price by basket range then dividing by total supply
* BU price accounts for oracle error
* As for the basket range - whenever one of the collaterals is missing (i.e. less than baskets needed) it estimates the value of anything above the min baskets held, and when doing that it estimates for oracle error as well.


Consider the following scenario:
* We have a basket composed of 1 ETH token and 1 USD token (cUSDCv2)
* cUSDCv2 defaults and the backup token AAVE-USDC kicks in
* Before trading rebalances things we have 0 AAVE-USDC
* This means that we'd be estimating the low price of the ETH we're accounting for margin of error at least twice:
    * Within the `basketRange()` we're dividing the ETH's `low` price by `buPriceHigh`
    * Then we multiply again by `buPriceLow`

(there's also some duplication within the `basketRange()` but that function isn't in scope, what is is scope is the additional margin of error when multiplying by `buPriceLow`).


_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-07-reserve-findings/issues/31_
