### Title
Unrestricted `CallDispatcher.dispatch` lets anyone drain any token/ETH balance left on the shared dispatcher - ([File: evm/src/utils/CallDispatcher.sol])

### Summary
`CallDispatcher` is a singleton, unprivileged relay contract used by `IntentGatewayV2` to execute solver/user-supplied calldata during `placeOrder` (predispatch) and `fillOrder` (output execution). Its `dispatch(bytes)` function has **no access control** — any address can call it and instruct the dispatcher to `call` arbitrary targets with arbitrary value, moving out whatever native ETH or ERC-20 balance the dispatcher currently holds. This mirrors the Illuminate `Converter` finding: a shared helper contract that can accumulate value and lets "anyone" redeem/move whatever is stuck in it.

### Finding Description
`CallDispatcher.dispatch` is external, with the only checks being that the call target has code and that the sub-call succeeds — no `onlyGateway`/`onlyOwner` gate exists: [1](#0-0) 

The dispatcher also has an unrestricted `receive()` so it can hold native ETH: [2](#0-1) 

This single dispatcher instance (`_params.dispatcher`) is shared by every order across the gateway. It is used to run:
- `order.predispatch.call` during `placeOrder`, after tokens are transferred into it: [3](#0-2) 
- `order.output.call` during `_execute` (called from fill logic), after which only the assets explicitly listed in `order.output.assets` are swept back to the gateway: [4](#0-3) 

The `_execute` sweep loop only iterates over `outputsLen` (i.e., `order.output.assets.length`) tokens. Any calldata execution that produces token balances or ETH the order didn't declare (e.g., DeFi routing that yields reward tokens, dust from swaps/LP unwraps, refunds from a downstream protocol, or a user simply mis-sending funds to the well-known dispatcher address) is left on the `CallDispatcher` indefinitely — the gateway has no sweep path for undeclared assets, and because `dispatch()` is public with no auth, **anyone** can subsequently call `CallDispatcher.dispatch()` directly with a `Call[]` that transfers those stray balances to themselves.

This is functionally identical to the reported `Converter` issue: a shared value-holding helper contract that (a) is not fully "polished" against leaking value it temporarily custodies, and (b) permits arbitrary redemption of whatever is accidentally/residually stuck in it by any caller.

### Impact Explanation
Because `CallDispatcher` is the single shared execution relay for the entire `IntentGatewayV2` deployment (used by every `placeOrder`/`fillOrder` across all users and orders), any ETH/ERC-20 balance it ever accumulates outside the exact atomic sweep windows is permanently exposed to theft by an unrelated, unprivileged actor. This can result in concrete loss of user/solver/protocol funds (theft of value), satisfying the Medium bar of "concrete theft ... of funds."

### Likelihood Explanation
Likelihood is realistic though not guaranteed on every order: it requires the dispatcher to end up holding a balance the current sweep logic does not account for (undeclared reward/dust tokens from `output.call` execution, a stuck/partial transaction, or a mistaken direct transfer to the well-known, publicly documented dispatcher address). Given `output.call` is attacker/solver-controlled calldata routed through arbitrary DeFi protocols, and the well-known dispatcher address is easy for anyone to target directly, this is a single-transaction, permissionless attack path once any residual balance exists — no special privilege is required to exploit it, only to observe a non-zero balance on the dispatcher (which is public on-chain state).

### Recommendation
- Restrict `CallDispatcher.dispatch()` to only be callable by registered `IntentGatewayV2` instance(s) (`onlyGateway`/allowlist of caller addresses), matching the "converter" pattern of gating redemption/movement of custodied funds.
- Alternatively, make the dispatcher single-use/ephemeral per call (e.g., deploy per order or self-destruct/settle strictly within the same transaction, disallowing any external interaction outside the calling gateway's tx).
- Extend `_execute`'s sweep to capture the full balance delta of any token touched by the executed calldata (not just the declared `order.output.assets`), similar to how `placeOrder`'s predispatch path already sweeps the dispatcher's *entire* balance rather than only the requested amount.

### Proof of Concept
1. A solver fills a cross-DEX order via `fillOrder`, whose `order.output.call` swaps through a router that also pays out an unlisted reward/bonus token (or leaves rounding dust) into `CallDispatcher`.
2. `_execute`'s sweep only sweeps the `outputsLen` tokens declared in `order.output.assets`; the reward/dust token balance remains on `CallDispatcher`.
3. Any third party — with no relationship to the order — calls `CallDispatcher.dispatch(abi.encode([Call({to: rewardToken, value: 0, data: transfer(attacker, balance)})]))` directly. Since `dispatch` has no caller restriction, the call succeeds and the stray tokens are transferred to the attacker.

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

**File:** evm/src/apps/IntentGatewayV2.sol (L236-290)
```text
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
