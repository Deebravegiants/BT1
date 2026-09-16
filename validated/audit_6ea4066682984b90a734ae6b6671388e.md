### Title
IntentGatewayV2 predispatch/postdispatch sweeps use the shared `CallDispatcher`'s *total* balance instead of a per-order delta, letting a caller claim tokens left behind by another user's order - ([File: evm/src/apps/IntentGatewayV2.sol])

### Summary
`IntentGatewayV2.placeOrder` and `IntentsBase._execute` route arbitrary predispatch/postdispatch calldata through a single, shared, stateless `CallDispatcher` contract. When sweeping the results of that calldata back into the gateway, both code paths measure the token's *entire current balance* on the dispatcher (`IERC20(token).balanceOf(dispatcher)` / `dispatcher.balance`) rather than the amount actually produced by the current order's own call. Because `CallDispatcher` is reused across all users' orders and its balance persists between transactions, any token left stranded there by one user's order (slippage, fee-on-transfer dust, an unlisted swap output, etc.) can be swept in full by an unrelated, later order that references the same token — exactly the "leftover token stolen by another user closing/placing an unrelated position" pattern from the AuraSpell report.

### Finding Description
`CallDispatcher.sol` is a minimal, permissionless relay contract with no access control and no per-caller isolation — it simply executes whatever `Call[]` it's given and holds whatever balance results: [1](#0-0) 

In `IntentGatewayV2.placeOrder`, when an order has predispatch calldata, the gateway pushes the declared predispatch assets to `dispatcher`, invokes the arbitrary call, and then sweeps input tokens back by reading `dispatcher`'s **full balance** for each input token/native asset — not the delta produced by this specific predispatch call: [2](#0-1) 

The same balance-of-the-shared-contract pattern is used again in `IntentsBase._execute`, which is invoked by both same-chain (`IntrinsicIntents._fillSameChain`) and cross-chain (`ExtrinsicIntents.fillOrder`) fills after solver-supplied calldata runs, sweeping `dispatcher`'s current balance of each output token/native asset back to the gateway: [3](#0-2) 

Because `dispatcher` is one shared, long-lived contract address (`_params.dispatcher`) used across every order and every user, any token balance that is not fully consumed or forwarded by a given order's calldata call (e.g., a swap that under-delivers, produces an unlisted token, or leaves dust due to fee-on-transfer behavior) stays parked on `CallDispatcher` after that transaction completes. The next unrelated caller who submits an order referencing that same token in `order.inputs` (predispatch) or `order.output.assets` (fill/execute) will have the *entire* stray balance swept and attributed to their own order:

- In `placeOrder`, if the swept balance exceeds `order.inputs[i].amount`, the excess is only logged as `DustCollected` but the whole balance is still physically moved into the gateway; if the swept balance (attacker's real contribution + stranded balance from other users) is between the attacker's actual minimal contribution and `order.inputs[i].amount`, `order.inputs[i].amount = received` is accepted at face value [4](#0-3) , letting an attacker declare a large `order.inputs[i].amount`, spend only a trivial amount executing the predispatch call, and rely on tokens left behind by prior orders to satisfy the `balance >= requiredAmount` check — effectively converting protocol/other-users' dust into their own escrowed, solver-redeemable order value.
- In `_execute`, the swept dust nominally lands back on the gateway itself (`address(this)`) rather than directly on a caller, but it still removes value that belonged to a specific prior order's unconsumed calldata output from the shared dispatcher and folds it into "protocol dust," bypassing accounting that should have flowed back to whichever order actually produced it.

This is structurally identical to the `AuraSpell#closePositionFarm` bug: an operation on a shared intermediary contract leaves residual tokens that are not scoped to the originating operation, and a later, unrelated caller's balance-based sweep captures the full contract balance rather than only the amount its own operation generated.

### Impact Explanation
An attacker can use crafted predispatch calldata (e.g., a minimal or manipulated swap) combined with a large declared `order.inputs[i].amount` to fraudulently inflate their escrowed order value using tokens that were never theirs, using stray balances left in the shared `CallDispatcher` by other users' orders. This constitutes theft/misappropriation of funds belonging to other users or the protocol's dust-sweep mechanism, and can be repeated deterministically whenever residual balances accumulate on the dispatcher (which is a normal, expected occurrence given fee-on-transfer tokens, slippage, and multi-asset swaps are explicitly supported use cases for predispatch/postdispatch calldata).

### Likelihood Explanation
High reachability: `placeOrder` and `fillOrder`/`_execute` are unprivileged, directly callable entry points reachable by any user via a single transaction with attacker-controlled `order` and `predispatch`/`output.call` fields. The shared `dispatcher` address is a fixed, publicly known contract (`_params.dispatcher`), so an attacker can monitor its token balances and time an order to arrive right after residue is left by another user's order, or even intentionally engineer their own prior order to leave dust and then sweep it with a second order.

### Recommendation
Compute swept amounts as a delta relative to a balance snapshot taken immediately before dispatching *this* order's calldata (as already correctly done later in the same function for `received` when comparing to `balancesBefore`), rather than reading the dispatcher's live/global balance to decide how much to transfer. Alternatively, make `CallDispatcher` calls atomic and self-contained per order (e.g., deploy an ephemeral dispatcher per order, or require the dispatcher to zero out/forward all balances at the end of every dispatch so no state persists between unrelated orders).

### Proof of Concept
1. User A places an order with predispatch calldata that, due to slippage/fee-on-transfer/an unlisted intermediate token, leaves 1,000 USDC sitting on the shared `CallDispatcher` contract after `placeOrder` completes (`evm/src/apps/IntentGatewayV2.sol:258-306`) — this is plausible any time predispatch involves a DEX swap or multi-hop unwrap.
2. Attacker B observes `IERC20(USDC).balanceOf(dispatcher) == 1000e6`.
3. Attacker B calls `placeOrder` with `order.inputs = [{token: USDC, amount: 1000e6}]` and predispatch calldata that trivially calls a no-op contract (or transfers a negligible amount of USDC to the dispatcher, e.g. 1 wei) to satisfy the predispatch-must-move-funds check.
4. In the sweep loop, `balance = IERC20(USDC).balanceOf(dispatcher)` reads ~1000e6 (mostly User A's stranded funds), passes `balance >= requiredAmount`, and the full balance is transferred to the gateway and attributed to B's order (`order.inputs[i].amount = received`).
5. Attacker B (or a colluding "solver") then fills/redeems this order, extracting 1,000 USDC that originated from User A's transaction, without B having contributed those funds.

### Citations

**File:** evm/src/utils/CallDispatcher.sol (L25-62)
```text
contract CallDispatcher is ICallDispatcher {
    /**
     * @dev error thrown when the target is not a contract.
     */
    error NotContract(address target);

    /**
     * @dev error thrown when a call fails.
     */
    error CallFailed(address target, bytes result);

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
