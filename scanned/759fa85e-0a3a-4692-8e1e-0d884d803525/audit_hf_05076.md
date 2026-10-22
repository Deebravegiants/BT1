# [M] Liquidations will leave dust when repaying

## Summary
Severity: Medium
Contest weight: 0.6231
Dataset id: 23091
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Market::liquidate() gets the maximum assets to liquidate from Auditor::checkLiquidation(). Then, when repaying maturities, when they have expired, it calculates how much principal of the maturity it has to liquidate to take into account the penalty rate and liquidate at most maxRepayAssets. However, there is rounding in this process that means the actual repay assets will be smaller than maxRepayAssets, which means the liquidatee will have dust collateral. Thus, it will be impossible to clear the bad debt, even if liquidated again later. In Market::liquidate(), it calculates the actual repay has:
```solidity
uint256 debt = position + position.mulWadDown((block.timestamp - maturity) * penaltyRate);
actualRepay = debt > maxAssets ? maxAssets.mulDivDown(position, debt) : maxAssets;
```
When debt > maxAssets, it will round down in the calculation, liquidating less assets than the maximum and leaving the liquidatee with some dust making it impossible to clear the bad debt. Internal pre-conditions 1. Liquidatee has more debt than collateral and expired maturities. External pre-conditions None. Attack Path 1. Liquidatee borrows at maturity and lets it expire, not repaying the debt until it grows bigger than the collateral. 2. Liquidator liquidates but it is never possible to fully clear the collateral so clearBadDebt() will never be called. When there are expired maturities and the debt is bigger than the collateral clearBadDebt() will not be called, not even if liquidated successively.

## Proof of Concept
```solidity
function test_POC_ClearBadDebt_Impossible_DueToDust() external {
uint256 maxVal = type(uint256).max;
market.deposit(10000 ether, address(this));
vm.startPrank(BOB);
market.deposit(100 ether, BOB);
market.borrowAtMaturity(4 weeks, 60e18, maxVal, BOB, BOB);
vm.stopPrank();
vm.startPrank(ALICE);
market.deposit(10, ALICE);
market.borrowAtMaturity(4 weeks, 1, maxVal, ALICE, ALICE);
vm.stopPrank();
skip(20 weeks);
(uint256 coll, uint256 debt) = market.accountSnapshot(BOB);
console.log(coll);
console.log(debt);
vm.startPrank(ALICE);
market.liquidate(BOB, 100_000 ether, market);
vm.stopPrank();
(coll, debt) = market.accountSnapshot(BOB);
console.log(coll);
console.log(debt);
vm.startPrank(ALICE);
market.liquidate(BOB, 100_000 ether, market);
vm.stopPrank();
(coll, debt) = market.accountSnapshot(BOB);
console.log(coll);
console.log(debt);
vm.startPrank(ALICE);
vm.expectRevert(); // ZERO WITHDRAW
market.liquidate(BOB, 100_000 ether, market);
vm.stopPrank();
}
```

## Recommendation
No data
