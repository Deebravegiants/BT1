# [M] users_can_enable_tokenids_as_collateral_even_if_they_do_not_own_any_of_the_erc-6909_supply

## Summary
Severity: Medium
Contest weight: 0.0000
Dataset id: 23483
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
It is possible for users to enable tokenIds that that they do not own as collateral. Based on the cur‑rent remediated logic, it does not appear possible for this to be further weaponized beyond the blocking of liquidations, as described in C-01, stemming from the incorrect implementation ERC721WrapperBase::normalizedToFull as described in H-02. That said, this ability for a borrower to add a tokenId as collateral for which they have zero ERC-6909 balance should be explicitly forbidden. Liquidators who do not already own a share of the position but need to enable the tokenId as collateral to pass account liquidity checks should still be able to do so by utilizing the deferred checks of EVC batch calls.

## Proof of Concept
```solidity
function test_enableCollateralPoC() public {
    LiquidityParams memory params = LiquidityParams({
        tickLower: TickMath.MIN_TICK + 1,
        tickUpper: TickMath.MAX_TICK - 1,
        liquidityDelta: -19999
    });
    (tokenId,,) = boundLiquidityParamsAndMint(params, borrower);
    startHoax(borrower);
    wrapper.underlying().approve(address(wrapper), tokenId);
    // avoid wrapping such that ERC-6909 total supply remains zero
    assertEq(wrapper.totalSupply(tokenId), 0);
    address borrower2 = makeAddr("borrower2");
    startHoax(borrower2);
    assertEq(wrapper.getEnabledTokenIds(borrower2).length, 0);
    wrapper.enableTokenIdAsCollateral(tokenId);
    assertEq(wrapper.getEnabledTokenIds(borrower2).length, 1);
}
```

## Recommendation
Consider requiring a non‑zero ERC‑6909 balance when enabling collateral:

```solidity
error TokenIdNotOwnedByBorrower(uint256 tokenId, address sender);
function enableTokenIdAsCollateral(uint256 tokenId) public returns (bool enabled) {
    address sender = _msgSender();
    enabled = _enabledTokenIds[sender].add(tokenId);
    if (totalTokenIdsEnabledBy(sender) > MAX_TOKENIDS_ALLOWED) revert
        MaximumAllowedTokenIdsReached();,!
    // New check to ensure the borrower owns the tokenId
    if (balanceOf(sender, tokenId) == 0) revert TokenIdNotOwnedByBorrower(tokenId, sender);
    if (enabled) emit TokenIdEnabled(sender, tokenId, true);
}
```
