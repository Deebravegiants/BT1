## Analysis Result

I found a valid analog. It reproduces the same root-cause pattern as the reported `AccountV1::skim` bug: crediting a caller based on the *raw current balance* of a shared/pooled contract instead of an isolated, per-caller expected delta — allowing appropriation of value that was never contributed by the caller.

### Title
Shared `CallDispatcher` balance is swept in full and blindly credited to the caller's escrow in `placeOrder`, letting an attacker steal stray/leftover token balances - (File: `evm/src/apps/IntentGatewayV2.sol`)

### Summary
`IntentGatewayV2.placeOrder()`'s predispatch path sweeps the **entire current balance** of `_params.dispatcher` (a single, permanently shared `CallDispatcher` instance used by every order in the protocol) for each input token, and credits whatever it collects as that order's own "actually received" input amount, which is then escrowed under the caller's commitment.

### Finding Description
In the predispatch branch of `placeOrder`, for every declared input token the code reads the dispatcher's **raw balance**, not the amount actually produced by *this* order's predispatch call: [1](#0-0) 

```solidity
uint256 balance = IERC20(token).balanceOf(dispatcher);
if (balance < requiredAmount) revert InvalidInput();
transferCalls[i] = Call({
    to: token, value: 0,
    data: abi.encodeWithSelector(IERC20.transfer.selector, address(this), balance)
});
```

The whole `balance` (not `balance - balanceBeforeThisCall`) is swept from the dispatcher into the gateway, and the delta observed on `address(this)` becomes `order.inputs[i].amount`: [2](#0-1) 

That amount is then escrowed for the caller's commitment with no further verification that it came from the caller's own predispatch execution: [3](#0-2) 

The `CallDispatcher` is a single stateless, shared executor contract used by *all* orders and both predispatch/postdispatch flows across the entire gateway — it has a public `receive()` and its ERC-20 balance can be topped up by anyone at any time (a plain `transfer` needs no permission): [4](#0-3) 

Because the sweep is keyed only on `order.inputs`, not on `order.predispatch.assets`, any token left in the dispatcher that is *not* enumerated by a prior order's `order.inputs`/`order.output.assets` is never collected as protocol dust and is never zeroed out — it simply accumulates in the dispatcher, unaccounted for anywhere in contract storage. The postdispatch sweep in `_execute` has the identical raw-balance pattern: [5](#0-4) 

This is the exact same bug class as the reported `skim` issue: the contract treats "whatever raw balance sits in a shared pool" as belonging to the current operation, with no check that it was actually contributed by the current caller/order, and no accounting distinguishing legitimately-owned funds from stray/attacker-donated/leftover balances.

### Impact Explanation
Any user can place an order whose `order.inputs` lists a token that already has a stray balance sitting in the shared `CallDispatcher` (from a prior order's predispatch/postdispatch execution that produced a residual not enumerated by that order's `inputs`/`output.assets`, or from any account directly `transfer()`-ing tokens to the publicly-known dispatcher address). By supplying a trivial/no-op `predispatch.call` and `predispatch.assets` (even donating a negligible amount themselves), the attacker's `placeOrder` call sweeps the dispatcher's **full** balance of that token, which is credited entirely as their own escrowed input (`_orders[commitment][token]`). The attacker can then cancel the order and reclaim tokens they never actually deposited, i.e., outright theft of value that belongs to no on-chain account (protocol dust) or, worse, to another user whose in-flight predispatch/postdispatch call happened to leave residual balance in the same shared dispatcher. This directly drains value from the IntentGateway ecosystem without any privilege, health check, or auction-state check — same severity class as the reported High-severity `skim` finding (unauthorized appropriation of funds via balance-vs-accounting mismatch).

### Likelihood Explanation
Reachable by any unprivileged address calling the public, non-privileged `placeOrder()` — no special permission, auction participation, or governance role required. The only precondition is that the shared `CallDispatcher` holds an uncollected residual balance of some token, which can arise from ordinary predispatch/postdispatch flows (DEX swap dust, reward-token side effects, rounding) that are not enumerated in `order.inputs`/`order.output.assets`, or can be manufactured directly by anyone sending tokens to the well-known dispatcher address. Given the dispatcher is a long-lived singleton shared across the entire protocol's lifetime, dust accumulation is expected to occur naturally over time, making exploitation straightforward once any such balance exists.

### Recommendation
Never credit a caller based on the dispatcher's absolute balance. Instead:
1. Snapshot the dispatcher's balance for each input token **before** executing `order.predispatch.call`, and only sweep/credit `balanceAfter - balanceBefore` (the amount actually produced by this call), not the dispatcher's total balance.
2. Track any genuinely leftover/un-enumerated dispatcher balance explicitly as protocol dust (with a `DustCollected` event and a mechanism to sweep it under governance only), rather than silently leaving it available for the next arbitrary caller to claim.
3. Apply the same before/after-per-call snapshot discipline to the postdispatch sweep in `IntentsBase._execute`.

### Proof of Concept
1. Deploy/observe the shared `CallDispatcher` address used by `IntentGatewayV2` (`_params.dispatcher`), same contract for all orders and predispatch/postdispatch calls.
2. Wait for (or trigger) a legitimate order whose predispatch call produces a residual token `T` balance in the dispatcher that isn't part of that order's `order.inputs` array (e.g., DEX swap dust, cashback token, or rounding remainder) — this balance is never swept and never tracked anywhere.
3. Attacker calls `placeOrder` with:
   - `predispatch.assets`: a trivial donation (e.g., 1 wei of token `T`, or any token/ETH amount ≥ 0 satisfying the non-zero check).
   - `predispatch.call`: a no-op/benign call satisfying `ICallDispatcher.dispatch`.
   - `order.inputs[0] = {token: T, amount: <dispatcher's current full balance of T>}`.
4. `placeOrder` reads `IERC20(T).balanceOf(dispatcher)` — which includes the leftover residual from step 2 plus the attacker's negligible donation — and sweeps 100% of it to the gateway, crediting the full amount as `order.inputs[0].amount`.
5. `_orders[commitment][T]` is now credited with tokens the attacker never actually contributed.
6. Attacker cancels the order (`cancelOrder`) and receives the full escrowed amount back via `_withdraw`, realizing a net gain equal to the stolen residual balance. [6](#0-5) [7](#0-6)

### Citations

**File:** evm/src/apps/IntentGatewayV2.sol (L235-311)
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

**File:** evm/src/apps/IntentGatewayV2.sol (L363-373)
```text
        // Phase 3: Credit escrow.
        for (uint256 i; i < inputsLen;) {
            address token = address(uint160(uint256(order.inputs[i].token)));
            // Reject duplicate input tokens
            if (_orders[commitment][token] != 0) revert InvalidInput();
            _orders[commitment][token] = reducedInputs[i].amount;

            unchecked {
                ++i;
            }
        }
```

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

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L498-533)
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
```

**File:** evm/src/apps/intentsv2/IntrinsicIntents.sol (L159-180)
```text
    function _cancelSameChain(Order calldata order, bytes32 commitment) internal {
        if (order.user != bytes32(uint256(uint160(msg.sender)))) revert Unauthorized();

        uint256 inputsLen = order.inputs.length;
        TokenInfo[] memory remainingTokens = new TokenInfo[](inputsLen);
        bool hasEscrow = false;
        for (uint256 i; i < inputsLen;) {
            address token = address(uint160(uint256(order.inputs[i].token)));
            uint256 escrowed = _orders[commitment][token];
            if (escrowed > 0) hasEscrow = true;
            remainingTokens[i] = TokenInfo({token: order.inputs[i].token, amount: escrowed});
            unchecked {
                ++i;
            }
        }
        if (!hasEscrow) revert UnknownOrder();

        WithdrawalRequest memory body =
            WithdrawalRequest({commitment: commitment, tokens: remainingTokens, beneficiary: order.user});

        _withdraw(body, true, true);
    }
```
