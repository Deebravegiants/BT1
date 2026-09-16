## Finding

The Flooring Protocol incident traced the exploit to its "peripheral/multi-call contract" — a helper contract meant to be invoked only in the context of specific privileged flows, but which itself carried no restriction on who could call it, letting an attacker drive it directly. Hyperbridge's Intent Gateway has a structurally identical component: `CallDispatcher`.

### Title
Unauthenticated `CallDispatcher.dispatch()` allows anyone to drain any token/native balance held by the shared peripheral contract - (File: `evm/src/utils/CallDispatcher.sol`)

### Summary
`CallDispatcher` is the peripheral multi-call contract that `IntentGatewayV2` (and other apps referencing the same `_params.dispatcher`) uses to execute arbitrary order calldata (`predispatch`/`output.call`) and to sweep resulting balances. Its `dispatch()` entrypoint has no access control whatsoever, exactly mirroring the "peripheral/multi-call contract" bug class cited in the report.

### Finding Description
`CallDispatcher.dispatch()` is `external` with no modifier and no `msg.sender` check: [1](#0-0) 

It also unconditionally accepts native token transfers via `receive()`: [2](#0-1) 

`IntentsBase._execute` and `IntentGatewayV2.placeOrder` route arbitrary user/solver-supplied calldata (`order.predispatch.call`, `order.output.call`) through this same shared instance, and only sweep back the token set explicitly enumerated in `order.output.assets` / `order.inputs` — any other token or native residual produced by the arbitrary call (e.g., a DEX swap through an unlisted intermediate token, or dust) is left sitting in `CallDispatcher`: [3](#0-2) [4](#0-3) 

Because `dispatch()` accepts any caller and any `Call[]`, whoever notices such a balance — or a stray/accidental token/ETH transfer sent directly to `CallDispatcher`'s address — can call `dispatch()` themselves with a `Call` routing that balance to their own address, with no relationship to any order, gateway, or governance authorization.

### Impact Explanation
Any unprivileged address reachable via a single transaction can extract any ERC-20 or native balance sitting in `CallDispatcher` at the time of the call: unswept dust from arbitrary predispatch/output DeFi routes (tokens outside the enumerated `order.output.assets`/`order.inputs` list), or direct/accidental transfers. Since the contract is shared infrastructure referenced by the Intent Gateway (and, per the wider codebase, potentially other apps configured with the same dispatcher address), this is a protocol-wide unauthenticated fund-extraction path, not scoped to a single order or user — matching the "concrete theft of funds" bar.

### Likelihood Explanation
High: no privileged role, proof, or relayer status is required — a plain call to `dispatch(bytes)` with an ABI-encoded `Call[]` suffices. Any solver/order calldata that routes through a token not accounted for in the sweep list, or any direct transfer to the contract, creates an immediately exploitable window since there is no time-lock, owner-only sweep, or caller restriction protecting the balance.

### Recommendation
Restrict `CallDispatcher.dispatch()` to only the registered gateway/app contracts that are authorized to route calls through it (e.g., an allow-list of caller addresses set at deployment, or making the dispatcher a per-gateway single-purpose contract rather than a shared unauthenticated one). Additionally, ensure the sweep logic in `_execute`/`placeOrder` accounts for arbitrary tokens (not just the enumerated set) so dust cannot accumulate unswept in a permissionless contract.

### Proof of Concept
1. Any order's `output.call` or `predispatch.call` performs a DeFi route (e.g., a multi-hop swap) that yields a small amount of an intermediate token not present in `order.output.assets`/`order.inputs`.
2. `_execute`/`placeOrder`'s sweep loop only checks balances for tokens in the enumerated asset list, so the intermediate token remains in `CallDispatcher`. [5](#0-4) 
3. An attacker (any EOA) calls `CallDispatcher.dispatch(abi.encode([Call({to: intermediateToken, value: 0, data: abi.encodeWithSelector(IERC20.transfer.selector, attacker, balance)})]))` directly.
4. `dispatch()` executes the call with no authorization check, transferring the token balance to the attacker. [1](#0-0)

### Citations

**File:** evm/src/utils/CallDispatcher.sol (L36-39)
```text
    /**
     * @dev Receive function to accept ETH transfers
     */
    receive() external payable {}
```

**File:** evm/src/utils/CallDispatcher.sol (L44-62)
```text
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

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L498-545)
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
    }
```

**File:** evm/src/apps/IntentGatewayV2.sol (L235-290)
```text
        if (order.predispatch.call.length > 0 && order.predispatch.assets.length > 0) {
            address dispatcher = _params.dispatcher;

            uint256 assetsLen = order.predispatch.assets.length;
            for (uint256 i; i < assetsLen;) {
                address token = address(uint160(uint256(order.predispatch.assets[i].token)));
                uint256 amount = order.predispatch.assets[i].amount;
                if (amount == 0) revert InvalidInput();

                if (token == address(0)) {
                    if (amount > msgValue) revert InsufficientNativeToken();
                    msgValue -= amount;

                    _sendValue(dispatcher, amount);
                } else {
                    IERC20(token).safeTransferFrom(msg.sender, dispatcher, amount);
                }

                unchecked {
                    ++i;
                }
            }

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

```
