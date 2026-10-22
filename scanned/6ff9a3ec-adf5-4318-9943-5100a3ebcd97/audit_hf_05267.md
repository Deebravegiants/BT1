# [H] fees_can_become_stuck_in_uniswapv4wrapper

## Summary
Severity: High
Contest weight: 0.0000
Dataset id: 23480
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When a modification is made to Uniswap V4 position liquidity, such as in the case of a partial UniswapV4Wrapper unwrap which decreases liquidity, any outstanding fees are also transferred and required to be completely settled. For multiple holders of a given ERC-6909 tokenId, a proportional share is escrowed and paid out during a given holder's next interaction with the wrapper contract. However, there exists an edge case in which fees can become stuck in UniswapV4Wrapper if the final holder performs a full unwrap through the overload which transfers the underlying position directly to the caller.

Consider the following scenario:
• Alice has full ownership of a position tokenId1.  
• Assume LP fees have accrued in the position.  
• Alice partially unwraps tokenId1 to remove a portion of the underlying liquidity.  
• This accrues LP fees corresponding to the remainder of the position to the UniswapV4Wrapper.  
• Alice max borrows and later gets fully liquidated.  
• The liquidator fully unwraps the tokenId1 position and received the underlying NFT but loses their share of the previously-accrued fees.  
• The liquidator removes all the liquidity of the underlying position they received for the full liquidation, and burns the position.  
• As a result, it is impossible to retrieve the fees remaining in the wrapper because the position has been burnt and is impossible to mint the same tokenId again.

## Proof of Concept
```solidity
function test_finalLosesFeesPoC() public {
int256 liquidityDelta = -19999;
uint256 swapAmount = 100_000 * unit0;
LiquidityParams memory params = LiquidityParams({
tickLower: TickMath.MIN_TICK + 1,
tickUpper: TickMath.MAX_TICK - 1,
liquidityDelta: liquidityDelta
});
(uint256 tokenId1,,) = boundLiquidityParamsAndMint(params);
startHoax(borrower);
wrapper.underlying().approve(address(wrapper), tokenId1);
wrapper.wrap(tokenId1, borrower);
wrapper.enableTokenIdAsCollateral(tokenId1);
address borrower2 = makeAddr("borrower2");
wrapper.transfer(borrower2, tokenId1, wrapper.FULL_AMOUNT() * 5 / 10);
//swap so that some fees are generated
swapExactInput(borrower, address(token0), address(token1), swapAmount);
(uint256 expectedFees0Position1, uint256 expectedFees1Position1) =
MockUniswapV4Wrapper(payable(address(wrapper))).pendingFees(tokenId1);
console.log("Expected Fees Position 1: %s, %s", expectedFees0Position1, expectedFees1Position1);
startHoax(borrower);
wrapper.unwrap(
23
borrower,
tokenId1,
borrower,
wrapper.balanceOf(borrower, tokenId1),
bytes("")
);
console.log("Wrapper balance of currency0: %s", currency0.balanceOf(address(wrapper)));
startHoax(borrower2);
wrapper.unwrap(borrower2, tokenId1, borrower2);
console.log("Wrapper balance of currency0: %s", currency0.balanceOf(address(wrapper)));
if (currency0.balanceOf(address(wrapper)) > 0 && wrapper.totalSupply(tokenId1) == 0) {
console.log("Fees stuck in wrapper!");
}
}
```

## Recommendation
Check whether there are any outstanding fees accrued for a given tokenId when performing a full unwrap and transfer these to the recipient along with the underlying NFT. This would also have the added benefit of avoiding dust accumulating in the contract which may arise from floor rounding during proportional share calculations using small ERC-6909 balances.
