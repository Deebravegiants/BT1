# [M] First depositor can lock the quote target value

## Summary
Severity: Medium
Contest weight: 0.5933
Dataset id: 20423
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When the initial deposit occurs, it is possible for the quote target to be set to 0. This situation significantly impacts other LPs as well. Even if subsequent LPs deposit substantial amounts, the quote target remains at 0 due to multiplication with this zero value. 0 QUOTE_TARGET value will impact the swaps that pool facilities
When the first deposit happens, QUOTE_TARGET is set as follows:
```solidity
if (totalSupply == 0) {
    // case 1. initial supply
    // The shares will be minted to user
    shares = quoteBalance < DecimalMath.mulFloor(baseBalance, _I_)
    ? DecimalMath.divFloor(quoteBalance, _I_)
    : baseBalance;
    // The target will be updated
    _BASE_TARGET_ = uint112(shares);
    _QUOTE_TARGET_ = uint112(DecimalMath.mulFloor(shares, _I_));
}
```
In this scenario, the 'shares' value can be a minimum of 1e3, as indicated here:
link to code snippet.
This implies that if someone deposits minuscule amounts of quote token and base token, they can set the QUOTE_TARGET to zero because the mulFloor operation uses a scaling factor of 1e18:
```solidity
function mulFloor(uint256 target, uint256 d) internal pure returns (uint256) {
    return target * d / (10 ** 18);
}
```
Should the quote target become 0, subsequent deposits will not increase due to the multiplication with "0" on the quote target. This situation is highly problematic because the swaps depend on the value of the quote target:
43e196fc0185abffe6304d/dodo-gassaving-pool/contracts/GasSavingPool/impl/GSPFunding.sol#L74-L75
```solidity
// @review 0 + (0 * something) = 0! doesn't matter what amount has been deposited !
_QUOTE_TARGET_ = uint112(uint256(_QUOTE_TARGET_) +
(DecimalMath.mulFloor(uint256(_QUOTE_TARGET_), mintRatio)));
```
Here a PoC shows that if the first deposit is tiny the QUOTE_TARGET is 0. Also, whatever deposits after goes through the QUOTE_TARGET still 0 because of the multiplication with 0!
```solidity
function test_StartWithZeroTarget() external {
    // tapir deposits tiny amounts to make quote target 0
    vm.startPrank(tapir);
    dai.safeTransfer(address(gsp), 1 * 1e5);
    usdc.transfer(address(gsp), 1 * 1e5);
    gsp.buyShares(tapir);
    console.log("Base target", gsp._BASE_TARGET_());
    console.log("Quote target", gsp._QUOTE_TARGET_());
    console.log("Base reserve", gsp._BASE_RESERVE_());
    console.log("Quote reserve", gsp._QUOTE_RESERVE_());
    // quote target is indeed 0!
    assertEq(gsp._QUOTE_TARGET_(), 0);
    vm.stopPrank();
    // hippo deposits properly
    vm.startPrank(hippo);
    dai.safeTransfer(address(gsp), 1000 * 1e18);
    usdc.transfer(address(gsp), 10000 * 1e6);
    gsp.buyShares(hippo);
    console.log("Base target", gsp._BASE_TARGET_());
    console.log("Quote target", gsp._QUOTE_TARGET_());
    console.log("Base reserve", gsp._BASE_RESERVE_());
    console.log("Quote reserve", gsp._QUOTE_RESERVE_());
    // although hippo deposited 1000 USDC as quote tokens, target is still 0 due to multiplication with 0
    assertEq(gsp._QUOTE_TARGET_(), 0);
}
```
Test result and logs:
Since the quote target is important and used when pool deciding the swap math I will label this as high.

## Recommendation
According to the quote tokens decimals, multiply the quote token balance with the proper decimal scalor.
