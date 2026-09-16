## Analysis

The reported bug class — an ERC20 `transfer` that can return `false` on failure instead of reverting, with the caller treating the raw call as successful — has a direct, reachable analog in Hyperbridge's Intent Gateway sweep logic.

### Root cause

`CallDispatcher.dispatch` only checks the low-level `call` success flag, never the ERC20 boolean return value:

```solidity
(bool success, bytes memory result) = to.call{value: call.value}(call.data);
if (!success) revert CallFailed(to, result);
``` [1](#0-0) 

`CallDispatcher.dispatch` has **no access control** — any address can call it directly. [2](#0-1) 

The `IntentGatewayV2` and `IntentsBase` contracts build sweep `Call`s that invoke raw `IERC20.transfer.selector` (not `safeTransfer`) through this dispatcher, in both the predispatch escrow-sweep path in `placeOrder` and the postdispatch sweep in `_execute`:

```solidity
transferCalls[i] = Call({
    to: token,
    value: 0,
    data: abi.encodeWithSelector(IERC20.transfer.selector, address(this), balance)
});
...
ICallDispatcher(dispatcher).dispatch(abi.encode(transferCalls));
``` [3](#0-2) [4](#0-3) 

The Tron deployment has the same pattern: [5](#0-4) 

Note that elsewhere in the same contracts (`_withdraw`, `send`, `onAccept`, direct `IERC20` calls) `SafeERC20.safeTransfer`/`safeTransferFrom` is used correctly — only the `Call`-encoded sweeps routed through `CallDispatcher` bypass this protection. [6](#0-5) 

### Title
Silent-failing ERC20 `transfer` in Intent Gateway sweep calls lets tokens strand in the unrestricted `CallDispatcher`, stealable by anyone — (File: evm/src/utils/CallDispatcher.sol, evm/src/apps/IntentGatewayV2.sol, evm/src/apps/intentsv2/IntentsBase.sol)

### Summary
`CallDispatcher.dispatch` executes arbitrary `Call[]` and treats a call as successful whenever the low-level `.call` does not revert, without inspecting the ERC20 boolean return value. `IntentGatewayV2.placeOrder` (predispatch sweep) and `IntentsBase._execute` (postdispatch sweep) build sweep calls using raw `IERC20.transfer.selector` — not `SafeERC20.safeTransfer` — and dispatch them through this unchecked path.

### Finding Description
When the input or output token of an order is an ERC20 implementation that returns `false` on failure instead of reverting (e.g. old-style tokens such as ZRX/EURS, or any token that pauses/blacklists an address and returns `false`), the `to.call(data)` in `CallDispatcher.dispatch` still returns `success = true` because the token contract itself never reverted. The gateway's accounting (escrowed `order.inputs[i].amount`, `DustCollected` emission) proceeds as if the tokens were moved from the `CallDispatcher` to the gateway, but the tokens actually remain stuck on the `CallDispatcher` contract's balance.

Because `CallDispatcher.dispatch` has no `onlyOwner`/`onlyGateway`/`restrict` modifier — it is a fully public, shared, permissionless dispatch target — any address can subsequently call `CallDispatcher.dispatch()` directly with a `Call` that transfers out the stranded token balance to themselves. This converts a silent-transfer failure into outright theft of the escrowed/dust funds, on top of desynchronizing the gateway's internal escrow bookkeeping from the dispatcher's actual balance.

### Impact Explanation
Concrete theft of user/solver funds: tokens that fail to move during a predispatch escrow sweep (`IntentGatewayV2.placeOrder`) or a postdispatch dust sweep (`IntentsBase._execute`, reachable from any `fillOrder` call with output calldata) can be permanently redirected by any third party calling the shared `CallDispatcher` directly, since its `dispatch` function is unauthenticated and the tokens sit unaccounted for there. This satisfies the "concrete theft ... of funds" bar for a valid analog.

### Likelihood Explanation
Reachable by any unprivileged user submitting a single `placeOrder` (predispatch calldata + assets) or any solver's `fillOrder` (output calldata), i.e. a single submitted transaction, no privileged role required. It only requires that one of the escrowed/output tokens is a non-reverting-on-failure ERC20 (a well-documented, non-exotic token category — the same class cited in the source report), or is temporarily paused/blacklisted for the gateway/dispatcher address at sweep time.

### Recommendation
- Change the sweep `Call.data` encoding in `evm/src/apps/IntentGatewayV2.sol`, `evm/src/apps/intentsv2/IntentsBase.sol`, and the Tron equivalent to use `SafeERC20.safeTransfer`-equivalent calldata (or have `CallDispatcher` decode and validate ERC20 return data length/value for `transfer`/`transferFrom` selectors).
- Restrict `CallDispatcher.dispatch` so it cannot be invoked by arbitrary third parties, or ensure it never holds residual balances across calls (e.g., self-destruct-style sweep-and-zero pattern) so a stranded balance from a failed transfer cannot be swept by an unrelated caller.

### Proof of Concept
1. An order's predispatch/output asset is a token `T` whose `transfer` returns `false` on failure (e.g., paused, blacklisted recipient, or insufficient balance in some legacy implementations) rather than reverting.
2. User calls `IntentGatewayV2.placeOrder` with a predispatch call that leaves `T` on the `CallDispatcher`; the subsequent sweep `Call` (`abi.encodeWithSelector(IERC20.transfer.selector, address(this), balance)`) is dispatched via `ICallDispatcher(dispatcher).dispatch(...)`.
3. `T.transfer` returns `false` without reverting; `CallDispatcher.dispatch`'s `(bool success,) = to.call(...)` still yields `success = true`, so no revert occurs.
4. The gateway records `received = 0` (balance unchanged) yet the pre-existing `balance` of `T` remains sitting on `CallDispatcher`.
5. Any external address calls `CallDispatcher.dispatch(abi.encode([Call({to: T, value: 0, data: transfer(attacker, balance)})]))` directly — this succeeds since `dispatch` is unauthenticated — draining the stranded `T` balance to the attacker.

### Citations

**File:** evm/src/utils/CallDispatcher.sol (L25-61)
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

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L451-469)
```text
    function _withdraw(WithdrawalRequest memory body, bool isRefund, bool finalize) internal {
        address beneficiary = address(uint160(uint256(body.beneficiary)));
        if (finalize) _filled[body.commitment] = beneficiary;

        uint256 len = body.tokens.length;
        for (uint256 i; i < len; i++) {
            address token = address(uint160(uint256(body.tokens[i].token)));
            uint256 amount = body.tokens[i].amount;
            if (amount == 0) continue;

            uint256 escrowed = _orders[body.commitment][token];
            if (escrowed == 0) revert UnknownOrder();

            _orders[body.commitment][token] = escrowed - amount;
            if (token == address(0)) {
                _sendValue(beneficiary, amount);
            } else {
                IERC20(token).safeTransfer(beneficiary, amount);
            }
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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L416-449)
```text
            // Transfer tokens from call dispatcher back to IntentGateway
            Call[] memory transferCalls = new Call[](inputsLen);
            for (uint256 i; i < inputsLen;) {
                address token = address(uint160(uint256(order.inputs[i].token)));
                uint256 requiredAmount = order.inputs[i].amount;
                uint256 balance;

                if (token == address(0)) {
                    balance = address(dispatcher).balance;
                    if (balance < requiredAmount) revert InsufficientNativeToken();
                    transferCalls[i] = Call({to: address(this), value: balance, data: ""});
                } else {
                    balance = IERC20(token).balanceOf(dispatcher);
                    if (balance < requiredAmount) revert InvalidInput();
                    transferCalls[i] = Call({
                        to: token,
                        value: 0,
                        data: abi.encodeWithSelector(IERC20.transfer.selector, address(this), balance)
                    });
                }

                uint256 dust = balance - requiredAmount;
                if (dust > 0) emit DustCollected(token, dust);

                // Store reduced amount (after protocol fees) in escrow
                _orders[commitment][token] += reducedInputs[i].amount;

                unchecked {
                    ++i;
                }
            }

            // Execute transfer calls from call dispatcher
            ICallDispatcher(dispatcher).dispatch(abi.encode(transferCalls));
```
