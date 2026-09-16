## Title
`CallDispatcher.dispatch()` has no caller restriction, letting anyone drain any ETH/ERC20 balance the shared dispatcher holds - (File: `evm/src/utils/CallDispatcher.sol`)

### Summary
`CallDispatcher.dispatch()` is `external` with no access-control modifier at all, mirroring the root cause of the reported JOJO bug (`JOJOFlashLoan` callable by anyone to route arbitrary calls using contract-held funds). `CallDispatcher` is a single, shared, permanently-deployed utility contract used by `IntentGatewayV2`, `HyperFungibleToken`, `WrappedHyperFungibleToken`, and their upgradeable variants to execute untrusted `Call[]` batches against its own balance. It also exposes a public `receive() external payable`, so it can hold a native-token balance at any time, and any caller can invoke `dispatch()` to move that balance (or any ERC20 balance the contract holds) to an address of their choosing.

### Finding Description
`CallDispatcher.dispatch` decodes an attacker-supplied `Call[]` and executes each entry with `to.call{value: call.value}(call.data)`, with `call.value` drawn from the dispatcher's own balance: [1](#0-0) 

There is no `onlyOwner`, `onlyGateway`, or reentrancy/caller check anywhere in the contract, and `receive()` is unconditionally payable, so any address can fund the contract and any address can call `dispatch()` to move funds out of it — exactly the missing-modifier pattern the external report calls out (`onlyJusdBank` was proposed there; the analogous `onlyGateway`/immutable-caller check is absent here).

The contract is explicitly designed as a *shared* singleton — its address is published on the "contract addresses" page and reused by every `IntentGatewayV2`/`HyperFungibleToken` deployment on a chain: [2](#0-1) 

Normal protocol flows transfer assets into the dispatcher and then immediately sweep the *entire* balance back out within the same atomic call (e.g. `IntentGatewayV2`/`IntentsBase._execute` and `placeOrder`), which is why routine dust is not usually left behind: [3](#0-2) [4](#0-3) 

But because `dispatch()` itself carries no restriction, any ETH sent to the dispatcher's `receive()` — whether by user error, a partially-failed native transfer, or any other source outside the atomic gateway flow — sits exposed: whoever notices it can immediately call `dispatch()` with a `Call{to: attacker, value: <balance>, data: ""}` and take it, since the function performs the `.call{value: ...}` using the contract's own held balance and never checks `msg.sender`.

### Impact Explanation
Any native-token balance (or stray ERC20 balance from a direct `transfer()` to the dispatcher address) held by this shared, always-deployed contract can be permissionlessly swept by any third party, resulting in concrete theft of funds that were not intended for that caller. Because the dispatcher is reused across all `IntentGatewayV2` and `HyperFungibleToken`/`WrappedHyperFungibleToken` instances on a chain, this is a protocol-wide, permanently reachable drain vector rather than an isolated per-app issue.

### Likelihood Explanation
The trigger requires the dispatcher to hold a balance outside of the tightly-atomic gateway sweep sequences — via its open `receive()` function or a mistaken direct ERC20 transfer to its published address — which is a plausible real-world occurrence for a widely-referenced, documented contract address. Once any balance exists, exploitation is a single, permissionless, zero-cost call to `dispatch()`.

### Recommendation
Restrict `dispatch()` to trusted callers only (e.g., an immutable allow-list of registered gateway/app addresses set at construction, or a per-call authorization scheme), and/or make `CallDispatcher` never hold residual balances by design (reject unsolicited `receive()` ETH, or require `dispatch()` to be called atomically by the same caller that funded it within the same transaction). At minimum, add an `onlyAuthorizedCaller`-style modifier analogous to the `onlyJusdBank` fix proposed in the referenced report.

### Proof of Concept
1. Any address sends native ETH directly to the deployed `CallDispatcher` address (its `receive()` accepts unconditionally): [5](#0-4) 
2. An unrelated attacker calls `dispatch(abi.encode([Call({to: attacker, value: <dispatcher.balance>, data: ""})]))`.
3. `dispatch()` executes `to.call{value: call.value}(call.data)` with no caller check, transferring the dispatcher's entire native balance to the attacker: [6](#0-5)

### Citations

**File:** evm/src/utils/CallDispatcher.sol (L36-62)
```text
    /**
     * @dev Receive function to accept ETH transfers
     */
    receive() external payable {}

    /**
     *  @dev reverts if the target is not a contract or if any of the calls reverts.
     */
    function dispatch(bytes memory encoded) external {
        Call[] memory calls = abi.decode(encoded, (Call[]));
        uint256 callsLen = calls.length;
        for (uint256 i = 0; i < callsLen; ++i) {
            Call memory call = calls[i];
            uint32 size;
            address to = call.to;
            assembly {
                size := extcodesize(to)
            }

            if (size == 0) {
                revert NotContract(to);
            }

            (bool success, bytes memory result) = to.call{value: call.value}(call.data);
            if (!success) revert CallFailed(to, result);
        }
    }
```

**File:** docs/content/developers/evm/hyper-fungible-token/overview.mdx (L94-98)
```text
### Security

The `CallDispatcher` executes calls in its own context (not via `delegatecall`), so the HFT contract's storage is never at risk. If any call in the array reverts, the entire `onAccept` handler reverts — including the token mint/unlock. The request can then be retried by any relayer until the timeout expires. If no successful execution occurs before the timeout, the request times out and the sender is eligible for a refund on the source chain. Token approvals in the `Call[]` should use exact amounts rather than unlimited allowances, since the dispatcher contract holds tokens temporarily during execution.

Existing `CallDispatcher` deployments are listed on the [contract addresses](/developers/evm/contract-addresses/mainnet) page.
```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L498-544)
```text
    function _execute(Order calldata order, uint256 outputsLen) internal {
        if (order.output.call.length == 0) return;

        address dispatcher = _params.dispatcher;
        ICallDispatcher(dispatcher).dispatch(order.output.call);

        Call[] memory sweepCalls = new Call[](outputsLen);
        uint256 sweepCount = 0;

        for (uint256 i; i < outputsLen;) {
            address token = address(uint160(uint256(order.output.assets[i].token)));

            if (token == address(0)) {
                uint256 balance = dispatcher.balance;
                if (balance > 0) {
                    sweepCalls[sweepCount] = Call({to: address(this), value: balance, data: ""});
                    sweepCount++;
                    emit DustCollected(token, balance);
                }
            } else {
                uint256 balance = IERC20(token).balanceOf(dispatcher);
                if (balance > 0) {
                    sweepCalls[sweepCount] = Call({
                        to: token,
                        value: 0,
                        data: abi.encodeWithSelector(IERC20.transfer.selector, address(this), balance)
                    });
                    sweepCount++;
                    emit DustCollected(token, balance);
                }
            }

            unchecked {
                ++i;
            }
        }

        if (sweepCount > 0) {
            Call[] memory finalCalls = new Call[](sweepCount);
            for (uint256 i; i < sweepCount;) {
                finalCalls[i] = sweepCalls[i];
                unchecked {
                    ++i;
                }
            }
            ICallDispatcher(dispatcher).dispatch(abi.encode(finalCalls));
        }
```

**File:** evm/src/apps/IntentGatewayV2.sol (L258-311)
```text
            ICallDispatcher(dispatcher).dispatch(order.predispatch.call);

            // Build sweep calls and snapshot gateway balances before the sweep.
            Call[] memory transferCalls = new Call[](inputsLen);
            uint256[] memory balancesBefore = new uint256[](inputsLen);
            for (uint256 i; i < inputsLen;) {
                if (order.inputs[i].amount == 0) revert InvalidInput();
                address token = address(uint160(uint256(order.inputs[i].token)));
                uint256 requiredAmount = order.inputs[i].amount;

                if (token == address(0)) {
                    uint256 balance = address(dispatcher).balance;
                    if (balance < requiredAmount) revert InsufficientNativeToken();
                    transferCalls[i] = Call({to: address(this), value: balance, data: ""});
                    balancesBefore[i] = address(this).balance;
                } else {
                    uint256 balance = IERC20(token).balanceOf(dispatcher);
                    if (balance < requiredAmount) revert InvalidInput();
                    transferCalls[i] = Call({
                        to: token,
                        value: 0,
                        data: abi.encodeWithSelector(IERC20.transfer.selector, address(this), balance)
                    });
                    balancesBefore[i] = IERC20(token).balanceOf(address(this));
                }

                unchecked {
                    ++i;
                }
            }

            ICallDispatcher(dispatcher).dispatch(abi.encode(transferCalls));

            // Measure actual received, emit dust for excess, update order.inputs.
            for (uint256 i; i < inputsLen;) {
                address token = address(uint160(uint256(order.inputs[i].token)));
                uint256 received;
                if (token == address(0)) {
                    received = address(this).balance - balancesBefore[i];
                } else {
                    received = IERC20(token).balanceOf(address(this)) - balancesBefore[i];
                }

                if (received > order.inputs[i].amount) {
                    uint256 dust = received - order.inputs[i].amount;
                    emit DustCollected(token, dust);
                } else {
                    order.inputs[i].amount = received;
                }

                unchecked {
                    ++i;
                }
            }
```
