# [H] ERC6909 Transfer Calculation Error

## Summary
Severity: High
Contest weight: 0.0000
Dataset id: 23479
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
More value can be extracted by liquidations than expected due to incorrect transfer calculations when the violator does not own the total ERC-6909 supply for each tokenId enabled as collateral.

Given that the UniswapV3Wrapper and UniswapV4Wrapper contracts are not typical EVK vault collateral, it is necessary to have some method for calculating how much of the claim on the underlying collateral needs to be transferred from sender to receiver when a share transfer is execution. In the context of liquidation, this transfer is made from the violator to liquidator; however, note that it is also necessary to implement this functionality for transfers in the usual context.

This is achieved by `ERC721WrapperBase::transfer` which allows the caller to specify the amount to transfer in terms of the underlying collateral value:

```solidity
/// @notice For regular EVK vaults, it transfers the specified amount of vault shares from the sender to
/// the receiver,!
/// @dev For ERC721WrapperBase, transfers a proportional amount of ERC6909 tokens (calculated as
/// totalSupply(tokenId) * amount / balanceOf(sender)) for each enabled tokenId from the sender to the
/// receiver.
function transfer(address to, uint256 amount) external callThroughEVC returns (bool) {
    address sender = _msgSender();
    uint256 currentBalance = balanceOf(sender);
    uint256 totalTokenIds = totalTokenIdsEnabledBy(sender);
    for (uint256 i = 0; i < totalTokenIds; ++i) {
        uint256 tokenId = tokenIdOfOwnerByIndex(sender, i);
        _transfer(sender, to, tokenId, normalizedToFull(tokenId, amount, currentBalance));
    }
    return true;
}
```

`balanceOf(sender)` returns the sum value of each tokenId in unitOfAccount terms which is in turn used by `normalizedToFull()` to calculate the proportional amount of each ERC-6909 token enabled as collateral by the sender that should be transferred.

These calculations work as intended when a sender owns the total ERC-6909 token supply for a given tokenId; however, this breaks if the sender owns less than 100 % of a given tokenId and results in the corresponding calculations of ERC-6909 tokens to transfer being larger than they should be. This ultimately leads to the liquidator extracting more value in unitOfAccount than requested.

The source of this error is in the `normalizedToFull()` function:

```solidity
function normalizedToFull(uint256 tokenId, uint256 amount, uint256 currentBalance) public view returns (uint256) {
    // @audit => multiplying by the total ERC-6909 supply of the specified tokenId is incorrect
    return Math.mulDiv(amount, totalSupply(tokenId), currentBalance);
}
```

Here, the total supply of ERC-6909 tokens of the specified tokenId is erroneously used in the multiplication when this should instead be normalized to the actual amount of ERC-6909 tokens owned by the user.

## Proof of Concept
### Expected behavior (100 % ownership)

```solidity
function test_transferExpectedPoC() public {
    int256 liquidityDelta = -19999;
    LiquidityParams memory params = LiquidityParams({
        tickLower: TickMath.MIN_TICK + 1,
        tickUpper: TickMath.MAX_TICK - 1,
        liquidityDelta: liquidityDelta
    });
    (uint256 tokenId1,,) = boundLiquidityParamsAndMint(params);
    (uint256 tokenId2,,) = boundLiquidityParamsAndMint(params);
    startHoax(borrower);
    wrapper.underlying().approve(address(wrapper), tokenId1);
    wrapper.underlying().approve(address(wrapper), tokenId2);
    wrapper.wrap(tokenId1, borrower);
    wrapper.wrap(tokenId2, borrower);
    wrapper.enableTokenIdAsCollateral(tokenId1);
    wrapper.enableTokenIdAsCollateral(tokenId2);
    address borrower2 = makeAddr("borrower2");
    // @audit-info => borrower owns a 100% of ERC-6909 supply of each tokenId
    uint256 beforeLiquidationBalanceOfBorrower1 = wrapper.balanceOf(borrower);
    address liquidator = makeAddr("liquidator");
    uint256 transferAmount = beforeLiquidationBalanceOfBorrower1 / 2;
    wrapper.transfer(liquidator, transferAmount);
    uint256 finalBalanceOfBorrower1 = wrapper.balanceOf(borrower);
    // @audit-info => liquidated borrower got seized the exact amount of assets requested by the liquidator
    startHoax(liquidator);
    wrapper.enableTokenIdAsCollateral(tokenId1);
    wrapper.enableTokenIdAsCollateral(tokenId2);
    assertApproxEqAbs(wrapper.balanceOf(liquidator), transferAmount, ALLOWED_PRECISION_IN_TESTS);
}
```

### Unexpected behavior (partial ownership)

```solidity
function test_transferUnexpectedPoC() public {
    int256 liquidityDelta = -19999;
    LiquidityParams memory params = LiquidityParams({
        tickLower: TickMath.MIN_TICK + 1,
        tickUpper: TickMath.MAX_TICK - 1,
        liquidityDelta: liquidityDelta
    });
    (uint256 tokenId1,,) = boundLiquidityParamsAndMint(params);
    (uint256 tokenId2,,) = boundLiquidityParamsAndMint(params);
    startHoax(borrower);
    wrapper.underlying().approve(address(wrapper), tokenId1);
    wrapper.underlying().approve(address(wrapper), tokenId2);
    wrapper.wrap(tokenId1, borrower);
    wrapper.wrap(tokenId2, borrower);
    wrapper.enableTokenIdAsCollateral(tokenId1);
    wrapper.enableTokenIdAsCollateral(tokenId2);
    address borrower2 = makeAddr("borrower2");
    // @audit-info => liquidated borrower doesn't own 100% of both tokenIds
    wrapper.transfer(borrower2, tokenId1, wrapper.FULL_AMOUNT() / 2);
    uint256 beforeLiquidationBalanceOfBorrower1 = wrapper.balanceOf(borrower);
    address liquidator = makeAddr("liquidator");
    uint256 transferAmount = beforeLiquidationBalanceOfBorrower1 / 2;
    wrapper.transfer(liquidator, transferAmount);
    uint256 finalBalanceOfBorrower1 = wrapper.balanceOf(borrower);
    startHoax(liquidator);
    wrapper.enableTokenIdAsCollateral(tokenId1);
    wrapper.enableTokenIdAsCollateral(tokenId2);
    // @audit-issue => because liquidated borrower did not have 100% of shares for both tokenIds, the liquidator earned more than requested
    // @audit-issue => liquidated borrower got seized more assets than they should have
    assertApproxEqAbs(wrapper.balanceOf(liquidator), transferAmount, ALLOWED_PRECISION_IN_TESTS);
}
```

## Recommendation
Recommended Mitigation: On the `normalizedToFull()`, change the formula as follows:

```solidity
function normalizedToFull(uint256 tokenId, uint256 amount, uint256 currentBalance) public view returns (uint256) {
    // - return Math.mulDiv(amount, totalSupply(tokenId), currentBalance);
    // + return Math.mulDiv(amount, balanceOf(_msgSender(), tokenId), currentBalance);
}
```
