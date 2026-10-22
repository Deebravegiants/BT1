# [C] 5.1.3 swapOutallows overwrite of token balance

## Summary
Severity: Critical
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Critical Risk
**Context:** StableSwapFacet.sol#L266-L281, SwapUtils.sol#L740-L781, SwapUtils.sol#L417-L
**Description:** TheStableSwapFacethas the functionswapExactOut()where a user could supply the sameas-
setInaddress asassetOut, which means theTokenIndexes fortokenIndexFromandtokenIndexTofunction
swapOut()are the same.
In functionswapOut() a temporay array is used to store balances. When updating such balances, first
self.balances[tokenIndexFrom]is updated and thenself.balances[tokenIndexTo]is updated afterwards.
However whentokenIndexFrom == tokenIndexTothe second update overwrites the first update, causing token
balances to be arbitrarily lowered. This also skews the exchange rates, allowing for swaps where value can be
extracted.
Note: the protection against this problem is location in functiongetY(). However, this function is not called from
swapOut().
Note: the same issue exists inswapInternalOut(), which is called fromswapFromLocalAssetIfNeededForEx-
actOut()via_swapAssetOut(). However, via this route it is not possible to specify arbitrary token indexes. There-
fore, there isn’t an immediate risk here.


```
contract StableSwapFacet is BaseConnextFacet {
...
function swapExactOut(... ,address assetIn, address assetOut, ... ) ... {
return
s.swapStorages[canonicalId].swapOut(
getSwapTokenIndex(canonicalId, assetIn), // assetIn could be same as assetOut
getSwapTokenIndex(canonicalId, assetOut),
amountOut,
maxAmountIn
);
}
...
}
library SwapUtils {
function swapOut(..., uint8 tokenIndexFrom, uint8 tokenIndexTo, ... ) ... {
...
uint256[] memory balances = self.balances;
...
self.balances[tokenIndexFrom] = balances[tokenIndexFrom].add(dx).sub(dxAdminFee);
self.balances[tokenIndexTo] = balances[tokenIndexTo].sub(dy);// overwrites previous update if
,! From==To
...
}
function getY(..., uint8 tokenIndexFrom, uint8 tokenIndexTo, ... ) ... {
...
require(tokenIndexFrom != tokenIndexTo, "compare token to itself");// here is the protection
...
}
}
```
Below is a proof of concept which shows that thebalancesof index 3 can be arbitrarily reduced.
//SPDX-License-Identifier: MIT
pragma solidity 0.8.14;
import "hardhat/console.sol";
contract test {
uint[] balances = new uint[](10);
function swap(uint8 tokenIndexFrom,uint8 tokenIndexTo,uint dx) public {
uint dy=dx;// simplified
uint256[] memory mbalances = balances;
balances[tokenIndexFrom] = mbalances[tokenIndexFrom] + dx;
balances[tokenIndexTo] = mbalances[tokenIndexTo] - dy;
}
constructor() {
balances[3] = 100;
swap(3,3,10);
console.log(balances[3]);// 90
}
}

**Recommendation:** Add the following toswapExactOut()andswapInternalOut():
require(tokenIndexFrom != tokenIndexTo, "compare token to itself");

**Connext:** Solved in PR 1528.
**Spearbit:** Verified.
