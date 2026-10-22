# [M] When bad debts are cleared, there will be

## Summary
Severity: Medium
Contest weight: 0.7043
Dataset id: 22772
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the market, all funds should be tracked accurately, whether they are currently held, borrowed by borrowers, or repaid in the future. To ensure this, the market has a sophisticated tracking system that functions effectively. However, when bad debts are cleared, there will be some untracked funds in the market. tracking system within the market primarily monitors funds within the variable involved.

First, there are extraordinary earnings, including variable backup fees, late collecting these earnings from extraordinary sources and subsequently distributing them gradually and smoothly. For this purpose, there is a earningsAccumulator variable.
```solidity
function depositAtMaturity(
    uint256 maturity,
    uint256 assets,
    uint256 minAssetsRequired,
    address receiver
) external whenNotPaused whenNotFrozen returns (uint256 positionAssets) {
    earningsAccumulator += backupFee;
}
```
When users deposit funds into the variable pool, the floatingAssets increase by the deposited amounts as well as any additional earnings from the earnings accumulator.
```solidity
function afterDeposit(uint256 assets, uint256) internal override whenNotPaused whenNotFrozen {
    updateFloatingAssetsAverage();
    uint256 treasuryFee = updateFloatingDebt();
    uint256 earnings = accrueAccumulatedEarnings();
    floatingAssets += earnings + assets;
    depositToTreasury(treasuryFee);
    emitMarketUpdate();
}
```
Funds borrowed by variable rate borrowers are tracked using the floatingDebt floatingBackupBorrowed variable. Additionally, there is an unassignedEarnings variable for each maturity pool, which represents upcoming fees from borrowers. These earnings are added to the floatingAssets whenever there are changes in the market, such as borrowers repaying their debt, depositors withdrawing their funds etc.
```solidity
function depositAtMaturity(
    uint256 maturity,
    uint256 assets,
    uint256 minAssetsRequired,
    address receiver
) external whenNotPaused whenNotFrozen returns (uint256 positionAssets) {
    floatingAssets += backupEarnings;
}
```
While this variable is important, it is not directly involved in the tracking system.

Let's describe the vulnerability. A user deposits 5 DAI into the DAI market. When clearing the bad debt, the amount is deducted from the earnings accumulator.
```solidity
function clearBadDebt(address borrower) external {
    if (totalBadDebt != 0) {
        earningsAccumulator -= totalBadDebt;
        emit SpreadBadDebt(borrower, totalBadDebt);
    }
}
```
maturity, and the penalty fee from this is added to the earnings accumulator.
```solidity
function noTransferRepayAtMaturity(
    uint256 maturity,
    uint256 positionAssets,
    uint256 maxAssets,
    address borrower,
    bool canDiscount
) internal returns (uint256 actualRepayAssets) {
    if (block.timestamp < maturity) {
        if (canDiscount) {
            ...
        } else {
            actualRepayAssets = debtCovered;
        }
    } else {
        actualRepayAssets = debtCovered + debtCovered.mulWadDown((block.timestamp - maturity) * penaltyRate);
        // all penalties go to the earnings accumulator
        earningsAccumulator += actualRepayAssets - debtCovered;
    }
}
```
Consequently, the DAI market has enough earningsAccumulator for clearing upcoming bad debt in the test. (see below log)
console2.log("floatingAssets before clear bad debt ==> ", market.floatingAssets());
console2.log("floatingDebt before clear bad debt ==> ", market.floatingDebt());
console2.log("floatingBackupBorrowed before clear bad debt ==> ", market.floatingBackupBorrowed());
console2.log("earningsAccumulator before clear bad debt ==> ", market.earningsAccumulator());
console2.log("owed weth balance before clear bad debt ==> ", principal_before, fee_before);
console2.log("calculated dai balance before clear bad debt ==> ", calculatedBalanceBefore);
console2.log("dai balance before clear bad debt ==> ", asset.balanceOf(address(market)));

Now this user borrows 1 DAI from the DAI market at a specific maturity. At this point, there is no bad debt in the market and the current tracking values are as follows:
floatingAssets before clear bad debt ==> 5005767123287671232800
floatingDebt before clear bad debt ==> 0
floatingBackupBorrowed before clear bad debt ==> 0
earningsAccumulator before clear bad debt ==> 112859178081957033645
owed weth balance before clear bad debt ==> 7671232876712328
calculated dai balance before clear bad debt ==> 5117626301369628266445
dai balance before clear bad debt ==> 5117626301369628266445

The current DAI balance is equal to floatingAssets - floatingDebt - floatingBackupBorrowed + earningsAccumulator. Everything is correct.

Now, consider 1 DAI equals to 5000 WETH. Given sufficient collateral, this user can borrow 5000 WEHT from the WETH market. If the price of DAI drops to 1000 WETH, this user can be liquidated.
unassignedEarnings of that maturity pool.
```solidity
function borrowAtMaturity(
    uint256 maturity,
    uint256 assets,
    uint256 maxAssets,
    address receiver,
    address borrower
) external whenNotPaused whenNotFrozen returns (uint256 assetsOwed) {
    {
        uint256 backupDebtAddition = pool.borrow(assets);
        if (backupDebtAddition != 0) {
            uint256 newFloatingBackupBorrowed = floatingBackupBorrowed + backupDebtAddition;
            depositToTreasury(updateFloatingDebt());
            if (newFloatingBackupBorrowed + floatingDebt > floatingAssets.mulWadDown(1e18 - reserveFactor)) {
                revert InsufficientProtocolLiquidity();
            }
        }
    }
    {
        // if account doesn't have a current position, add it to the list
        if (position.principal == 0) {
            Account storage account = accounts[borrower];
        }
        // calculate what portion of the fees are to be accrued and what portion goes to earnings accumulator
        (uint256 newUnassignedEarnings, uint256 newBackupEarnings) = pool.distributeEarnings(
            chargeTreasuryFee(fee),
            assets
        );
        if (newUnassignedEarnings != 0) pool.unassignedEarnings += newUnassignedEarnings;
        collectFreeLunch(newBackupEarnings);
    }
}
```
These unassignedEarnings are later added to the floatingAssets whenever changes occur in the pool. However, when clearing bad debt, the sum of principal and fee is deducted from the earningsAccumulator if it's enough to cover the bad debt. The floatingBackupBorrowed is reduced as principal (means that these funds returns to the variable pool), but there is no provision for the fee.
```solidity
function clearBadDebt(address borrower) external {
    while (packedMaturities != 0) {
        if (packedMaturities & 1 != 0) {
            ...
        }
        packedMaturities >>= 1;
    }
    if (totalBadDebt != 0) {
        emit SpreadBadDebt(borrower, totalBadDebt);
    }
    emitMarketUpdate();
}
```
In reality, the fee is reflected in the unassignedEarnings of that maturity pool, requiring an appropriate mechanism to update these unassignedEarnings. If this user is the last user of this maturity pool, there is no way to convert these unassignedEarnings to the tracking system. Consequently, funds equal to the unassignedEarnings remain untracked and unused. Or if this user is not the last user of this maturity pool, these untracked unassignedEarnings can be allocated to late floatingAssets after clear bad debt ==> 5057139572755893855767
floatingDebt after clear bad debt ==> 0
floatingBackupBorrowed after clear bad debt ==> 0
earningsAccumulator after clear bad debt ==> 55421917808101804495
owed weth balance after clear bad debt ==> 0 0
calculated dai balance after clear bad debt ==> 5112561490563995660262
dai balance after clear bad debt ==> 5112569161796872372590
difference ==> 7671232876712328
cleared fee ==> 7671232876712328
unassignedEarnings ==> 7671232876712328

The difference between the actual DAI balance and tracked balance is equal to the unassignedEarnings.

Please add below test to the Market.t.sol.
```solidity
function testClearBadDebtBeforeMaturity() external {
    market.deposit(5 ether, address(this));
    market.deposit(5_000 ether, ALICE);
    marketWETH.deposit(100_000 ether, ALICE);
    uint256 maxVal = type(uint256).max;
    vm.prank(ALICE);
    market.borrowAtMaturity(4 weeks, 1_00 ether, maxVal, ALICE, ALICE);
    vm.warp(12 weeks);
    market.repayAtMaturity(4 weeks, maxVal, maxVal, ALICE);
    uint256 maturity_16 = 16 weeks;
    market.borrowAtMaturity(maturity_16, 1 ether, maxVal, address(this), address(this));
    (uint256 principal_before, uint256 fee_before) = market.positionOf(address(this), maturity_16);
    uint256 calculatedBalanceBefore = market.floatingAssets() - market.floatingDebt() - market.floatingBackupBorrowed() + market.earningsAccumulator();
    console2.log("floatingAssets before clear bad debt ==> ", market.floatingAssets());
    console2.log("floatingDebt before clear bad debt ==> ", market.floatingDebt());
    console2.log("floatingBackupBorrowed before clear bad debt ==> ", market.floatingBackupBorrowed());
    console2.log("earningsAccumulator before clear bad debt ==> ", market.earningsAccumulator());
    console2.log("owed weth balance before clear bad debt ==> ", principal_before, fee_before);
    console2.log("calculated dai balance before clear bad debt ==> ", calculatedBalanceBefore);
    console2.log("dai balance before clear bad debt ==> ", asset.balanceOf(address(market)));
    daiPriceFeed.setPrice(5_000e18);
    uint256 borrowAmount = 5000 ether;
    marketWETH.borrowAtMaturity(maturity_16, borrowAmount, borrowAmount * 2, address(this), address(this));
    daiPriceFeed.setPrice(1_000e18);
    weth.mint(ALICE, 1_000_000 ether);
    vm.prank(ALICE);
    weth.approve(address(marketWETH), maxVal);
    vm.prank(ALICE);
    marketWETH.liquidate(address(this), maxVal, market);
    (uint256 principal_after, uint256 fee_after) = market.positionOf(address(this), maturity_16);
    uint256 calculatedBalanceafter = market.floatingAssets() - market.floatingDebt() - market.floatingBackupBorrowed() + market.earningsAccumulator();
    console2.log("***************");
    console2.log("floatingAssets after clear bad debt ==> ", market.floatingAssets());
    console2.log("floatingDebt after clear bad debt ==> ", market.floatingDebt());
    console2.log("floatingBackupBorrowed after clear bad debt ==> ", market.floatingBackupBorrowed());
    console2.log("earningsAccumulator after clear bad debt ==> ", market.earningsAccumulator());
    console2.log("owed weth balance after clear bad debt ==> ", principal_after, fee_after);
    console2.log("calculated dai balance after clear bad debt ==> ", calculatedBalanceafter);
    console2.log("dai balance after clear bad debt ==> ", asset.balanceOf(address(market)));
    console2.log("***************");
    console2.log("difference ==> ", asset.balanceOf(address(market)) - calculatedBalanceafter);
    console2.log("cleared fee ==> ", fee_before);
    console2.log("unassignedEarnings ==> ", unassignedEarnings_after);
}
```
This vulnerability can happen under normal situation and there should be no untracked funds in the market. Nobody will detect these untracked funds and they won't be used.

## Recommendation
```solidity
function clearBadDebt(address borrower) external {
    if (msg.sender != address(auditor)) revert NotAuditor();
    floatingAssets += accrueAccumulatedEarnings();
    Account storage account = accounts[borrower];
    uint256 accumulator = earningsAccumulator;
    uint256 totalBadDebt = 0;
    uint256 maturity = packedMaturities & ((1 << 32) - 1);
    packedMaturities = packedMaturities >> 32;
    while (packedMaturities != 0) {
        if (packedMaturities & 1 != 0) {
            uint256 badDebt = position.principal + position.fee;
            if (accumulator >= badDebt) {
                RewardsController memRewardsController = rewardsController;
                if (address(memRewardsController) != address(0))
                    memRewardsController.handleBorrow(borrower);
                accumulator -= badDebt;
                totalBadDebt += badDebt;
                emit RepayAtMaturity(maturity, msg.sender, borrower, badDebt, badDebt);
            }
        }
        packedMaturities >>= 1;
    }
    if (account.floatingBorrowShares != 0 && (accumulator = previewRepay(accumulator)) != 0) {
        (uint256 badDebt, ) = noTransferRefund(accumulator, borrower);
        totalBadDebt += badDebt;
    }
    if (totalBadDebt != 0) {
        earningsAccumulator -= totalBadDebt;
        emit SpreadBadDebt(borrower, totalBadDebt);
    }
    emitMarketUpdate();
}
```
Or we need more sophisticated solution.
