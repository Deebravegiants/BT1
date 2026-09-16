### Title
Silent ERC20 sweep failures leave funds permanently stuck in the permissionless `CallDispatcher` - ([File: evm/src/utils/CallDispatcher.sol])

### Summary
`IntentGatewayV2`'s predispatch flow and `IntentsBase._execute` sweep tokens out of the shared `CallDispatcher` contract using low-level, unchecked `IERC20.transfer` calldata dispatched through `CallDispatcher.dispatch`. `CallDispatcher.dispatch` only checks that the low-level call did not revert — it never inspects/decodes the ERC20 return value. A non-standard ERC20 that returns `false` on failure instead of reverting (the classic ZRX-style token) will make the sweep call "succeed" from `CallDispatcher`'s point of view while the tokens never actually move. Because `CallDispatcher.dispatch` has **no access control**, any leftover balance stranded in it this way — or via any other partial-transfer non-reversion — becomes directly stealable by any third party who calls `dispatch()` themselves with a `Call` that transfers the token out.

### Finding Description
`CallDispatcher.dispatch` executes arbitrary `Call[]` sequences supplied by callers, and is a permissionless, externally callable function with no owner/caller restriction: [1](#0-0) 

It treats a call as successful purely based on the low-level `.call` return flag:
```
(bool success, bytes memory result) = to.call{value: call.value}(call.data);
if (!success) revert CallFailed(to, result);
```
This does not decode or verify the ERC20 boolean return value. For tokens like ZRX that return `false` on a failed `transfer`/`transferFrom` without reverting, this call will report `success = true` even though no tokens were moved.

`IntentGatewayV2.placeOrder`'s predispatch path builds exactly this kind of unchecked transfer call to sweep tokens from the shared `dispatcher` back to the gateway: [2](#0-1) 

Similarly, `IntentsBase._execute` (used by both same-chain and cross-chain fill paths for postdispatch calldata) builds sweep calls the same unchecked way and additionally emits `DustCollected` events based on the balance read *before* the sweep — it never re-checks that the sweep actually moved funds: [3](#0-2) 

In the `placeOrder` predispatch flow, the code does at least measure `balancesBefore`/`balancesAfter` diffs on the gateway side to compute `received`, but that only detects a shortfall in what the *gateway* obtained — it does nothing to recover the tokens that are actually still sitting in `dispatcher`. In `_execute`, there isn't even that after-the-fact reconciliation; the pre-sweep balance is trusted and reported as swept regardless of whether the low-level call's `success=true` corresponded to an actual token movement.

Because `dispatcher` is a shared, singleton, permissionless utility contract (any caller can invoke `dispatch()` directly, not just `IntentGatewayV2`), any token balance that ends up stuck in it — whether from a silently-failing non-standard ERC20 sweep, or from any other edge case that leaves a positive balance on `dispatcher` after a `dispatch()` sequence — is trivially drainable: an attacker simply calls `CallDispatcher.dispatch()` themselves with a `Call{to: token, data: abi.encodeWithSelector(IERC20.transfer.selector, attacker, balance)}`.

### Impact Explanation
This is a real theft/permanent-freezing-of-funds vector reachable by a single unprivileged transaction:
- If a user (or the protocol via configuration) places or fills an order that routes such a non-standard, non-reverting-on-failure ERC20 through the predispatch or postdispatch calldata path, the sweep-back call can silently no-op while `success=true`, stranding order-input or dust tokens in `CallDispatcher`.
- Since `CallDispatcher.dispatch` is unauthenticated, any third-party attacker monitoring the chain can immediately call `dispatch()` to pull the stranded balance to themselves, resulting in direct theft of user/protocol funds that were meant to be escrowed or returned.
- Even absent an attacker beating the intended flow, the tokens are permanently locked from the intended recipients since neither `IntentGatewayV2` nor `IntentsBase` ever re-attempts or reconciles a failed sweep from `dispatcher`.

This satisfies "concrete theft or permanent freezing of funds" via a single dispatched user transaction/order, which is in scope.

### Likelihood Explanation
Likelihood depends on whether an order can include or be filled using a token that returns `false` on failed transfer instead of reverting (or otherwise leaves a nonzero balance mismatch after `dispatch()`), and whether such tokens are permitted as `order.inputs`/`order.output.assets`/`predispatch.assets` tokens. Given `IntentGatewayV2`/`IntentsBase` accept arbitrary ERC20 addresses supplied by the order (there is no token allow-list evident in the reviewed code), and Fee-On-Transfer tokens are explicitly tested/supported (see `FeeOnTransferToken` test fixture), it is plausible that ZRX-style non-reverting tokens are equally reachable, making likelihood Medium — it requires a specific class of non-standard token to be used in an order, but no privileged action is needed to exploit the drain once funds are stranded.

### Recommendation
- Replace the raw `to.call(data)` return-value check in `CallDispatcher.dispatch` (or in the calling contracts' sweep-call construction) with a pattern that also validates the ERC20 boolean return data, e.g. use `SafeERC20.safeTransfer`/`safeTransferFrom` semantics instead of raw `abi.encodeWithSelector(IERC20.transfer.selector, ...)` for the sweep calls built in `IntentGatewayV2.placeOrder` and `IntentsBase._execute`.
- After every `CallDispatcher.dispatch` sweep, reconcile actual balances (as already partially done in `placeOrder`'s predispatch balance-diff check) and revert if the dispatcher still holds a nonzero balance for a token that was supposed to be fully swept, rather than trusting the low-level call's `success` flag or a pre-sweep balance snapshot.
- Add access control to `CallDispatcher.dispatch` (e.g., restrict callers to a registry of authorized calling contracts) so that any balance transiently held by the shared dispatcher cannot be drained by arbitrary third parties even in edge-case failure scenarios.

### Proof of Concept
1. Deploy (or use) an ERC20 token `T` whose `transfer`/`transferFrom` returns `false` on failure without reverting (ZRX-style semantics), and register/allow it as an order input/output token in `IntentGatewayV2`.
2. Construct an order whose `predispatch.assets` includes token `T`, with `predispatch.call` a no-op `Call[]` (as in the existing `FeeOnTransferToken` test pattern in `evm/tests/foundry/IntentGatewayV2SameChainTest.sol`).
3. Configure/trigger token `T` so the sweep-back `transfer(address(this), balance)` call executed via `CallDispatcher.dispatch` returns `false` (e.g., insufficient internal balance/blacklist condition) without reverting — the low-level call succeeds (`success = true`), so `CallDispatcher` does not revert, and `IntentGatewayV2.placeOrder` proceeds, leaving `T`'s balance stuck on the `dispatcher` contract instead of the gateway.
4. As an unrelated third-party account, call `CallDispatcher.dispatch(abi.encode([Call({to: T, value: 0, data: abi.encodeWithSelector(IERC20.transfer.selector, attacker, strandedBalance)})]))` directly — since `dispatch` has no access control, this succeeds and transfers the stranded `T` balance to the attacker.
5. Result: the attacker has stolen the order's escrowed input tokens that were meant to remain with the protocol/user, while `IntentGatewayV2`'s internal escrow accounting (`_orders[commitment][token]`) reflects a different (smaller or zero) amount than what was actually available — a permanent loss for the legitimate order participants.

(Note: I was not able to execute this PoC in a live environment or fully confirm whether `IntentGatewayV2`'s token allow-list, if any exists elsewhere in configuration/governance code not surfaced by the index, would block non-standard tokens from being used as order assets — this would need to be verified in a full Devin session with complete repository access.)

### Citations

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

**File:** evm/src/apps/IntentGatewayV2.sol (L273-289)
```text
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
