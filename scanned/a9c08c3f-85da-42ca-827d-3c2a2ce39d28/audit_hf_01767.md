# [M] Wrong index causes last depositor to always get execution fee refund if cancelFlow is called by keeper to cancel a withdrawal

## Summary
Severity: Medium
Contest weight: 0.8288
Dataset id: 9790
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The function PerpetualVault:cancelFlow:L419-422, can be called by the keeper to cancel the current flow. It will call the internal PerpetualVault:_cancelFlow:L1220-1242 function, which refunds the execution fee paid by the user who initialized the (latest) flow, now being canceled. The refund is being done by calling refundExecutionFee on the GmxProxy contract, using depositInfo[counter].owner and depositInfo[counter].executionFee as arguments. This will correctly identify the user in the case of a deposit, as the counter state will always be the index of the latest depositor. However, it will most likely be incorrect if the flow being canceled is a withdrawal, since the withdrawer’s index in the depositInfo mapping will not equal the current counter value unless they were also the latest depositor. If the withdrawal being canceled does not belong to the latest depositor, the user who was the last depositor will have their execution fee refunded instead. This will continue to happen each time a flow is canceled, meaning the lastest depositor can have their fee refunded many times over, while the withdrawers will not receive any refund.

The state variable depositInfo is used to track deposits.
The state variable counter in PerpetualVault:L94 increments each time a deposit is done, and when used to index the depositInfo mapping it will always reference the latest entry in the mapping/the last depositor.
```solidity
    //PerpetualVault L87-88  state variables
    uint256 counter;
    mapping(uint256 => DepositInfo) public depositInfo;
```
```solidity
    //PerpetualVault:deposit:L228 
    counter++;
```
_cancelFlow function contains the flawed code for handling the cancellation of a withdrawal flow:
```solidity
        //PerpetualVault:_cancelFlow:L1220-1242
        } else if (flow == FLOW.WITHDRAW) {
            try
                IGmxProxy(gmxProxy).refundExecutionFee(
                    depositInfo[counter].owner,          
                    depositInfo[counter].executionFee
                )
            {} catch {}
        }
```
The same arguments for refundExecutionFee are used both for canceling deposits and if the flow is a withdrawal.
This will be correct for the deposit case, and if the user currently withdrawing also made the last deposit.
If this is not the case, the data at index counter will belong to another user, and the refundExecutionFee function will refund them, and the withdrawer will get no refund.

Paid executionFees will be refunded to the wrong user. This is likely to happen frequently if cancelFlow is called regularly. While the NatSpec for cancelFlow states this should only be done for GMX positions, there is nothing stopping this from being done to vaults that have used DEX swaps (ParaSwap). If DEX swaps are used frequently by the keeper,
it could incentivize depositors to pay very large executionFees. This is because the fee will be repaid on deposit if only a DEX swap is used. And being the latest depositor with a large depositInfo[counter].executionFee would mean
getting repaid that amount every time a withdrawal is canceled.

## Proof of Concept
Add this code to test/PerpetualVault.t.sol as it uses fixtures from that file.
```solidity
    //using 2x vault as natspec states cancelflow should not be called for 1x long vaults
    function testRefundWithdrawalOnCancel() external {
        uint256 collateralTokensUsed = 1e10;

        //Bob deposit
        address bob = makeAddr("bob");
        payable(bob).transfer(1 ether);
        depositFixtureInto2x(bob, collateralTokensUsed);

        //open short position in vault
        MarketPrices memory prices = mockData.getMarketPrices();
        bytes[] memory data = new bytes[](0);
        data[0] = abi.encode(3380000000000000);
        address keeper = PerpetualVault(vault2x).keeper();
        vm.prank(keeper);
        PerpetualVault(vault2x).run(true, false, prices, data);
        GmxOrderExecuted2x(true);

        vm.prank(keeper);
        PerpetualVault(vault2x).runNextAction(prices, data);

        //Alice deposit
        address alice = makeAddr("alice");
        payable(alice).transfer(1 ether);
        depositFixtureInto2x(alice, collateralTokensUsed);

        //increase position in vault
        data[0] = abi.encode(3380000000000000);
        vm.prank(keeper);
        PerpetualVault(vault2x).runNextAction(prices, data);
        GmxOrderExecuted2x(true);
        vm.prank(keeper);

        // finalize deposit
        (PerpetualVault.NextActionSelector selector, ) = PerpetualVault(vault2x)
            .nextAction();
        assertEq(uint8(selector), 6);
        vm.prank(keeper);
        PerpetualVault(vault2x).runNextAction(prices, data);

        //eve deposit while active position and pays exection fee
        address eve = makeAddr("eve");
        payable(eve).transfer(1 ether);
        depositFixtureInto2x(eve, collateralTokensUsed);

        //finish deposit and increase position
        data[0] = abi.encode(3380000000000000);
        vm.prank(keeper);
        PerpetualVault(vault2x).runNextAction(prices, data);
        GmxOrderExecuted2x(true);

        // finalize deposit
        (selector, ) = PerpetualVault(vault2x).nextAction();
        assertEq(uint8(selector), 6);
        delete data;
        vm.prank(keeper);
        PerpetualVault(vault2x).runNextAction(prices, data);

        //skip locktime
        uint256 lockTime = 1;
        PerpetualVault(vault2x).setLockTime(lockTime);
        vm.warp(block.timestamp + lockTime + 1);

        //No next action and flow is none
        (selector, ) = PerpetualVault(vault2x).nextAction();
        assertEq(uint8(selector), 0);
        uint8 flow = uint8(PerpetualVault(vault2x).flow());
        assertEq(flow, 0);

        //get user deposit for bob and withdraw
        uint256[] memory depositIds = PerpetualVault(vault2x).getUserDeposits(
            bob
        );
        uint256 executionFee = PerpetualVault(vault2x).getExecutionGasLimit(
            false
        );
        vm.deal(bob, 1 ether);
        vm.prank(bob);
        // bob withdraws with executionFee
        PerpetualVault(vault2x).withdraw{value: executionFee * tx.gasprice}(
            bob,
            depositIds[0]
        );

        //asert flow is now withdraw
        flow = uint8(PerpetualVault(vault2x).flow());
        assertEq(flow, 3);

        GmxOrderExecuted2x(true);

        //balance of users before cancelling flow
        uint256 eveBalanceBefore = eve.balance;
        uint256 bobBalanceBefore = bob.balance;

        //keeper cancels bobs withdrawal
        vm.prank(keeper);
        PerpetualVault(vault2x).cancelFlow();

        //eve as the last depositor should have unchanged eth balance
        //and since bob's withdrawal was canceled he should have increased due to the refund
        assertTrue(eveBalanceBefore == eve.balance);            //these will fail
        assertTrue(bobBalanceBefore < bob.balance);
    }
```

## Recommendation
In withdraw function at the start of a withdrawal flow the state variable flowData is set to the depositId of the withdrawal.
```solidity
    //PerpetualVault:withdraw:L256
    flowData = depositId;
```
This can be used in PerpetualVault:_cancelFlow:L1220-1242 to get the correct index for depositInfo mapping.
```diff
        // _cancelFlow L1231
        } else if (flow == FLOW.WITHDRAW) {
            (uint256 depositId) = flowData;
            try
                IGmxProxy(gmxProxy).refundExecutionFee(
                    depositInfo[counter].owner,
                    depositInfo[counter].executionFee
                    depositInfo[depositId].owner,
                    depositInfo[depositId].executionFee
                )
            {} catch {}
        }
```
