# [M] Excess yield will be lost

## Summary
Severity: Medium
Reporter: hickuphh3
Source: https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L374-L404
Type: audit-issue

## Details
# Excess yield will be lost

## Summary
Any excess yield after full debt repayment will be lost.

## Vulnerability Detail
Alchemix distributes yield by increasing the credit limit of the depositor. Hence, when the debt is fully repaid, while there is still unmarked yield claims (ie. there is existing WETH deposited into `alchemist`), that yield is lost.

Another consequence of interpreting yield as withdrawable collateral is that excess yield will be taken as collateral from other depositors (issue #6).

## POC
I did a comparison to see if it was possible for `withdraw_underlying_to_claim` to claim more from the excess yield, but as expected, it remains the same.

Up to Step 2, where debt is fully repaid, and the vault's credit is zero, I branched off into:

### Scenario A
Mark all vault shares as claimable (all collateral withdrawn).

### Scenario B
Before shares are marked as claimable, simulate a harvest through donation, then perform the claim.

We can see that while the claimed amounts are the same, the credit in scenario B decreases to `-253056162340750`, which would be equivalent to about ~= 0.0002530 alETH.

```solidity
function testUnclaimedYield() public {
        uint256 depositAmt = 1e18;

        // admin makes a deposit
        vault.register_deposit(1, depositAmt);

        // fully pay off loan
        (int256 vaultDebt,) = alchemist.accounts(vaultAdd);
        alchemist.repay(
            address(weth),
            alchemist.normalizeDebtTokensToUnderlying(address(weth), uint256(vaultDebt)),
            vaultAdd
        );

        // credit will be zero
        (int256 credit, ) = alchemist.accounts(vaultAdd);
        assertEq(credit, 0);

        // take snapshot
        uint256 snapshot = vm.snapshot();

        // Mark all as claimable
        uint256 vaultShares;
        (vaultShares, ) = alchemist.positions(vaultAdd, yieldToken);
        vault.withdraw_underlying_to_claim(
            vaultShares,
            0
        );
        uint256 userClaimableAmt = vault.claimable_for_token(1);
        console.log("User claimable:", userClaimableAmt);

        // Revert snapshot
        vm.revertTo(snapshot);

        // Simulate harvest through donation
        vm.stopPrank();
        vm.startPrank(user2);
        alchemist.depositUnderlying(
            yieldToken,
            10e18,
            user2,
            0
        );
        alchemist.mint(4e18, user2);
        IERC20 debtToken = IERC20(alchemist.debtToken());
        debtToken.approve(address(alchemist), type(uint256).max);
        alchemist.donate(yieldToken, 4e18);

        (credit, ) = alchemist.accounts(vaultAdd);
        console.log("credit after harvest claimable:");
        console.logInt(credit);

        // check claimable amount after marking all as claimable
        vaultShares;
        (vaultShares, ) = alchemist.positions(vaultAdd, yieldToken);
        vault.withdraw_underlying_to_claim(
            vaultShares,
            0
        );
        userClaimableAmt = vault.claimable_for_token(1);
        console.log("User claimable:", userClaimableAmt);
    }
```
<img width="361" alt="image" src="https://user-images.githubusercontent.com/87458768/219596708-f7a7748e-fee5-4325-940b-e1cfc10c4a25.png">

## Impact
Any excess yield is lost because yield is interpreted as collateral to be withdrawn.

## Code Snippet
https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L374-L404

## Tool used
Foundry Framework, Manual Review

## Recommendation
Claims should be interpreted as debt to be minted instead of collateral to be withdrawn.
