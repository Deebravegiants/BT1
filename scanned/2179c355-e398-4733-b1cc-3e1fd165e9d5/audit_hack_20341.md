# [M] 5.2.12 IncorrectnewSpotPriceandnewDeltamay be obtained due to unsafe downcasts

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Medium Risk

**Context:** XykCurve.sol#L83 and XykCurve.sol#L

**Description:** When calculatingnewSpotPriceingetBuyInfo(), an unsafe downcast fromuint256intouint
may occur and silently overflow, leading to much less value fornewSpotPricethan expected.

```
function getBuyInfo(
uint128 spotPrice, uint128 delta, uint256 numItems,
uint256 feeMultiplier, uint256 protocolFeeMultiplier
) external pure override returns (
Error error, uint128 newSpotPrice, uint128 newDelta,
uint256 inputValue, uint256 tradeFee, uint256 protocolFee
)
{
...
// get the pair's virtual nft and token reserves
uint256 tokenBalance = spotPrice;
uint256 nftBalance = delta;
...
// calculate the amount to send in
uint256 inputValueWithoutFee = (numItems * tokenBalance) / (nftBalance - numItems);
...
// set the new virtual reserves
newSpotPrice = uint128(spotPrice + inputValueWithoutFee);// token reserve
...
}
```
Same happens when calculatingnewDeltaingetSellInfo():

```
function getSellInfo(
uint128 spotPrice, uint128 delta, uint256 numItems,
uint256 feeMultiplier, uint256 protocolFeeMultiplier
) external pure override returns (
Error error, uint128 newSpotPrice, uint128 newDelta,
uint256 outputValue, uint256 tradeFee, uint256 protocolFee
)
{
...
// get the pair's virtual nft and eth/erc20 balance
uint256 tokenBalance = spotPrice;
uint256 nftBalance = delta;
...
// set the new virtual reserves
newDelta = uint128(nftBalance + numItems);// nft reserve
...
```
**PoC**

Proof of concept about how this wouldn't revert but silently overflow:


```
import "hardhat/console.sol";
contract test{
constructor() {
uint256 a = type(uint128).max;
uint256 b = 2;
uint128 c = uint128(a + b);
console.log(c);// c == 1, no error
}
}
```
**Recommendation:** Check if the value would overflow before casting as is already done in other places. This can
also be done with libraries such as OpenZeppelin SafeCast

```
// set the new virtual reserves
+ uint256 _newDelta = nftBalance + numItems
+ if (_newDelta > type(uint128).max) {
+ return (Error.SPOT_PRICE_OVERFLOW, 0, 0, 0, 0, 0);
+ }
```
- newDelta = uint128(nftBalance + numItems); // nft reserve
+ newDelta = uint128(_newDelta ); // nft reserve

**Sudorandom Labs:** Solved in PR#42.

**Spearbit:** Verified that this is fixed by PR#42.
