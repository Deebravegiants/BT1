# [M] redeemUnderlying doesn't round up, can pro-

## Summary
Severity: Medium
Contest weight: 0.5950
Dataset id: 19943
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
All nwToken asset to underlying and back translations rounds down. This allows for
withdrawing more than supplying in a supply floor underlying amount, withdraw
ceiling amount manner.
Let's suppose it's nwETH, so underlying is ETH with 18 dp, token is cETH with 8 dp.
finalExchangeRate needs to have x = 28 dp in order to _convertToAsset's
underlyingAmount * EXCHANGE_RATE_PRECISION / finalExchangeRate having cETH's
(18 + 18 - x) = 8 dp result, and _convertToUnderlying's assetAmount *
finalExchangeRate / EXCHANGE_RATE_PRECISION having ETH's (8 + x - 18) = 18 dp
result.
Let's say finalExchangeRate = 200822050757246498024651213 (it's cETH rate on
mainnet as of time of this writing: https://etherscan.io/token/0x4ddc2d193948926d02f9b1fe9e1daa0718270ed5#readContract).
Bob calls mint() with msg.value = 1 eth, obtains underlyingAmount *
EXCHANGE_RATE_PRECISION / finalExchangeRate = 1e18 * 1e18 /
200822050757246498024651213 = 4979532856 nwETH, then calls
redeemUnderlying(1000000000150000000), which burns the same underlyingAmount
* EXCHANGE_RATE_PRECISION / finalExchangeRate = 1000000000150000000 * 1e18 /
200822050757246498024651213 = 4979532856 nwETH, providing Bob with free
150000000 wei.
Bob can obtain all excess funds from the contract this way as long as
_checkSupplyInvariant() allows.
Since that's excess funds only, setting the severity to be medium.
redeemUnderlying() calls _convertToAsset() to get nwToken amount from the
underlying amount requested:
te/contracts/external/adapters/nwToken.sol#L116-L127
function redeemUnderlying(uint redeemAmount) external nonReentrant override
returns (uint) {
if (redeemAmount == 0) return NO_ERROR;
require(finalExchangeRate != 0);
// Handles event emission, balance update and total supply update
super._burn(msg.sender, _convertToAsset(redeemAmount));
_transferUnderlyingToSender(redeemAmount);
_checkSupplyInvariant();
return NO_ERROR;
}
_convertToAsset() always rounds down:
te/contracts/external/adapters/nwToken.sol#L180-L182
function _convertToAsset(uint256 underlyingAmount) private view returns
(uint256) {
return underlyingAmount * EXCHANGE_RATE_PRECISION / finalExchangeRate;
}
I.e. the shares required for the given amount of underlying are rounded down and
so some amount of underlying within the same shared count can be obtained for
free.
```

## Recommendation
```solidity
_checkSupplyInvariant() looks to be handling the overall solvency of the contract.
To be on the safe side consider rounding up the number of shares required for a
given amount of underlying in redeemUnderlying().
```
