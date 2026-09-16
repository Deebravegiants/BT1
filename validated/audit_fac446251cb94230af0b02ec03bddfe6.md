### Title
Fee-on-transfer tokens cause escrow over-crediting in `IntentGatewayV2.placeOrder` predispatch path on Tron - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The Tron variant of `IntentGatewayV2.placeOrder` escrows a token amount that is computed from the *requested* input amount rather than the amount the gateway actually receives after the internal predispatch sweep transfer. If the escrowed token is a fee-on-transfer (FOT) token, the internal `IERC20.transfer` from the call dispatcher to the gateway silently reduces the amount actually credited to the gateway, but the contract's internal `_orders` accounting is still incremented by the pre-fee amount — the same class of bug as the referenced Slingshot finding, where a minimum/expected-amount check/accounting step happens *before* the value-decreasing transfer effect is realized.

### Finding Description
In `evm/tron/contracts/apps/IntentGatewayV2.sol::placeOrder`, in the predispatch branch, the gateway sweeps tokens from the call dispatcher back to itself: [1](#0-0) 

Specifically:
- `balance = IERC20(token).balanceOf(dispatcher)` is read (line 428).
- A `Call` is queued to `transfer(address(this), balance)` from the dispatcher to the gateway (lines 430-434), but this transfer is only *executed later* via `ICallDispatcher(dispatcher).dispatch(abi.encode(transferCalls))` at line 449.
- Immediately, before the transfer is even executed, `dust = balance - requiredAmount` is computed and `_orders[commitment][token] += reducedInputs[i].amount` credits the escrow ledger with the *requested* (fee-reduced by protocol fee only) amount — not with what the gateway will actually hold after the transfer completes.

For a fee-on-transfer token, `address(this)` will receive strictly less than `balance` once `transfer` executes, yet the escrow mapping `_orders[commitment][token]` has already been credited assuming full receipt of `reducedInputs[i].amount`. There is no post-transfer balance check (no `balanceOf(address(this))` before/after comparison), unlike the fixed main EVM contract: [2](#0-1) 

which explicitly snapshots `balancesBefore`, sweeps, then re-measures `IERC20(token).balanceOf(address(this)) - balancesBefore[i]` and mutates `order.inputs[i].amount` to the actual received value before computing the commitment/escrow. The Tron contract lacks this actual-received-amount reconciliation for the predispatch-swept-token case, so `_orders[commitment][token]` can be inflated beyond the gateway's real token balance for that order.

### Impact Explanation
The `_orders` mapping is the ledger `withdraw`/`_withdraw`-equivalent logic (`IntentsBase._withdraw` pattern, decrementing `_orders[commitment][token]` and transferring out on release/refund) relies on to release funds to solvers or refund users. If the ledger overstates what the gateway actually holds for orders funded via the predispatch path with an FOT token, later legitimate withdrawals/refunds for that token can fail (insufficient balance) or an earlier claimant can drain the real balance, leaving other orders' recorded escrow uncollectible — a permanent freeze/loss of funds for those users. This is reachable by any unprivileged user simply by calling `placeOrder` with a predispatch call routing an FOT token, i.e., a single submitted transaction from an ordinary intent placer.

### Likelihood Explanation
Likelihood depends on an order using the predispatch mechanism with a fee-on-transfer ERC-20 as an input token — a supported, permissionless configuration (the predispatch/postdispatch calldata feature is a documented core capability of `IntentGatewayV2`), and no special privileges or governance are required to trigger it.

### Recommendation
Mirror the fix already present in `evm/src/apps/IntentGatewayV2.sol`: snapshot `IERC20(token).balanceOf(address(this))` before dispatching the transfer calls and re-measure it after `ICallDispatcher(dispatcher).dispatch(abi.encode(transferCalls))` completes, then use that actual-received delta (not the pre-transfer `balance`/`requiredAmount`) both for dust accounting and for the amount credited to `_orders[commitment][token]`.

### Proof of Concept
1. User places an order via `placeOrder` with `predispatch.call` and `predispatch.assets` set, where the swept input token is a fee-on-transfer token.
2. In the predispatch sweep loop (lines 420-446), `balance = IERC20(token).balanceOf(dispatcher)` is read and `_orders[commitment][token] += reducedInputs[i].amount` is credited using the pre-fee requested amount.
3. `ICallDispatcher(dispatcher).dispatch(abi.encode(transferCalls))` executes the `transfer(address(this), balance)` call (line 449); due to the token's transfer fee, `address(this)` receives less than `balance`.
4. `_orders[commitment][token]` now records more tokens than the gateway physically holds for this order.
5. When this order (or another order sharing the same token) is later filled/cancelled and `_withdraw`/`withdraw` attempts to pay out the full recorded escrow, the gateway can run short of actual token balance for later claims, freezing funds for the affected order(s).

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L416-446)
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
```

**File:** evm/src/apps/IntentGatewayV2.sol (L260-299)
```text
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
```
