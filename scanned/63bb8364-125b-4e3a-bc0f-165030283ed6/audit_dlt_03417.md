# [M] `performanceFeeReceiver` cannot mint any performance fee shares even if TVL is dropped by only a very tiny amount

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-04-noya
Published: 2024-05-17
Source: https://github.com/code-423n4/2024-04-noya-findings/issues/1532
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2024-04-noya/blob/cc3854f634a72bd4a8b597021887088ca2d6d29f/contracts/accountingManager/AccountingManager.sol#L475-L488
https://github.com/code-423n4/2024-04-noya/blob/cc3854f634a72bd4a8b597021887088ca2d6d29f/contracts/accountingManager/AccountingManager.sol#L526-L541
https://github.com/code-423n4/2024-04-noya/blob/cc3854f634a72bd4a8b597021887088ca2d6d29f/contracts/accountingManager/AccountingManager.sol#L493-L500
https://github.com/code-423n4/2024-04-noya/blob/cc3854f634a72bd4a8b597021887088ca2d6d29f/contracts/accountingManager/AccountingManager.sol#L582-L588
https://github.com/code-423n4/2024-04-noya/blob/cc3854f634a72bd4a8b597021887088ca2d6d29f/contracts/accountingManager/AccountingManager.sol#L627-L630


# Vulnerability details

## Impact
After `preformanceFeeSharesWaitingForDistribution` is set through calling the following `recordProfitForFee` function, calling the `collectPerformanceFees` function below cannot mint `preformanceFeeSharesWaitingForDistribution` shares to `performanceFeeReceiver` until at least 12 hours have passed.

https://github.com/code-423n4/2024-04-noya/blob/cc3854f634a72bd4a8b597021887088ca2d6d29f/contracts/accountingManager/AccountingManager.sol#L475-L488
```solidity
    function recordProfitForFee() public onlyManager nonReentrant {
        storedProfitForFee = getProfit();
        profitStoredTime = block.timestamp;

        if (storedProfitForFee < totalProfitCalculated) {
            return;
        }

        preformanceFeeSharesWaitingForDistribution =
            previewDeposit(((storedProfitForFee - totalProfitCalculated) * performanceFee) / FEE_PRECISION);
        ...
    }
```

https://github.com/code-423n4/2024-04-noya/blob/cc3854f634a72bd4a8b597021887088ca2d6d29f/contracts/accountingManager/AccountingManager.sol#L526-L541
```solidity
    function collectPerformanceFees() public onlyManager nonReentrant {
        if (
            preformanceFeeSharesWaitingForDistribution == 0 || block.timestamp - profitStoredTime < 12 hours
                || block.timestamp - profitStoredTime > 48 hours
        ) {
            return;
        }

        _mint(performanceFeeReceiver, preformanceFeeSharesWaitingForDistribution);

        totalProfitCalculated = storedProfitForFee;
        ...
        preformanceFeeSharesWaitingForDistribution = 0;
    }
```

During such 12 hours, it is very likely that the TVL would fluctuate; when the TVL is dropped by only a very small amount, such as 1 wei, calling the `checkIfTVLHasDroped` function below would reset `preformanceFeeSharesWaitingForDistribution` and `profitStoredTime` because `currentProfit` has become only a tiny smaller than `storedProfitForFee`. Afterwards, calling the `collectPerformanceFees` function cannot mint any performance fee shares to `performanceFeeReceiver`. Later, after the `recordProfitForFee` function is called to set `preformanceFeeSharesWaitingForDistribution` again, the same situation can repeat since fluctuation of the crypto market within a 12 hour period is very normal. As a result, `performanceFeeReceiver` might not be able to mint any performance fee shares at all since any very small drop of the TVL can cause `preformanceFeeSharesWaitingForDistribution` to be reset.

https://github.com/code-423n4/2024-04-noya/blob/cc3854f634a72bd4a8b597021887088ca2d6d29f/contracts/accountingManager/AccountingManager.sol#L493-L500
```solidity
    function checkIfTVLHasDroped() public nonReentrant {
        uint256 currentProfit = getProfit();
        if (currentProfit < storedProfitForFee) {
            ...
            preformanceFeeSharesWaitingForDistribution = 0;
            profitStoredTime = 0;
        }
    }
```

https://github.com/code-423n4/2024-04-noya/blob/cc3854f634a72bd4a8b597021887088ca2d6d29f/contracts/accountingManager/AccountingManager.sol#L582-L588
```solidity
    function getProfit() public view returns (uint256) {
        uint256 tvl = TVL();
        if (tvl + totalWithdrawnAmount > totalDepositedAmount) {
            return tvl + totalWithdrawnAmount - totalDepositedAmount;
        }
        return 0;
    }
```

https://github.com/code-423n4/2024-04-noya/blob/cc3854f634a72bd4a8b597021887088ca2d6d29f/contracts/accountingManager/AccountingManager.sol#L627-L630
```solidity
    function TVL() public view returns (uint256) {
        return TVLHelper.getTVL(vaultId, registry, address(baseToken)) + baseToken.balanceOf(address(this))
            - depositQueue.totalAWFDeposit;
    }
```

## Proof of Concept
Please add the following test in `testFoundry\TestAccounting.sol`. This test will pass to demonstrate the described scenario.

```solidity
    function test_performanceFeeReceiverCannotMintAnyPerformanceFeeSharesEvenIfTVLIsDroppedByOnly1Wei() public {
        uint256 _amount = 10_000 * 1e6;
        _dealWhale(baseToken, address(owner), address(0x1AB4973a48dc892Cd9971ECE8e01DcC7688f8F23), _amount);

        vm.startPrank(owner);
        accountingManager.setFeeReceivers(
            withdrawFeeReceiver, address(performanceFeeReceiver), address(managementFeeReceiver)
        );

        SafeERC20.forceApprove(IERC20(USDC), address(accountingManager), _amount);
        accountingManager.deposit(address(owner), _amount, address(0));

        accountingManager.setFees(1e4, 1e5, 1e5);

        accountingManager.calculateDepositShares(10);

        vm.warp(block.timestamp + 35 minutes);

        accountingManager.executeDeposit(10, address(connector), "");

        vm.stopPrank();

        // simulate that accountingManager gains a profit
        _dealWhale(baseToken, address(accountingManager), address(0x1AB4973a48dc892Cd9971ECE8e01DcC7688f8F23), _amount);
        uint256 initialProfit = accountingManager.getProfit();

        vm.startPrank(owner);
        accountingManager.recordProfitForFee();

        // preformanceFeeSharesWaitingForDistribution is positive at this moment
        assertGt(accountingManager.preformanceFeeSharesWaitingForDistribution(), 0);

        vm.warp(block.timestamp + 13 hours - 12);

        // simulate that tvl is only dropped by 1 wei just before collectPerformanceFees function is called
        accountingManager.rescue(address(USDC), 1);
        assertEq(initialProfit - accountingManager.getProfit(), 1);

        // Alice calls checkIfTVLHasDroped function just before collectPerformanceFees function is called,
        //   which resets preformanceFeeSharesWaitingForDistribution to 0 even tvl is only dropped by 1 wei
        vm.startPrank(alice);
        accountingManager.checkIfTVLHasDroped();
        assertEq(accountingManager.preformanceFeeSharesWaitingForDistribution(), 0);

        vm.warp(block.timestamp + 13 hours);

        vm.startPrank(owner);

        // calling collectPerformanceFees function cannot mint any performance fee shares to performanceFeeReceiver
        accountingManager.collectPerformanceFees();
        assertEq(accountingManager.balanceOf(address(performanceFeeReceiver)), 0);
    }
```

## Tools Used
Manual Review

## Recommended Mitigation Steps
The `checkIfTVLHasDroped` function can be updated to recalculate `preformanceFeeSharesWaitingForDistribution` when `storedProfitForFee - currentProfit` is smaller than a reasonable small threshold; if `storedProfitForFee - currentProfit` is bigger than such threshold, `preformanceFeeSharesWaitingForDistribution` and `profitStoredTime` can still be reset.


## Assessed type

Other
