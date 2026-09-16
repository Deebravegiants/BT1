### Title
Malicious `predispatch` order can sweep pre-existing `CallDispatcher` token/ETH balance into the caller's own escrow - (File: evm/src/apps/IntentGatewayV2.sol)

### Summary
`IntentGatewayV2.placeOrder()` lets any caller include a `predispatch` step that routes funds through the shared `CallDispatcher` singleton before crediting `order.inputs` to escrow. The code snapshots and sweeps the **entire current balance** of the `CallDispatcher` for each input token, rather than only the amount that this specific order's `predispatch.call` produced, and credits that full amount to the caller's own escrowed order. This mirrors the Arrakis `ArrakisV2Router` bug class: a shared, publicly-reachable contract balance (analogous to the router's balance funded by a "malicious vault") is trusted and drained by an unprivileged, attacker-crafted call.

### Finding Description
In `placeOrder()`, when `order.predispatch.call.length > 0 && order.predispatch.assets.length > 0`:
1. The caller's `predispatch.assets` (self-declared, can be trivial/minimal) are transferred to the shared `dispatcher` address, and `order.predispatch.call` (attacker-controlled calldata, can be an empty `Call[]`) is executed via `ICallDispatcher(dispatcher).dispatch(...)`.
2. For each `order.inputs[i]`, the code reads `balance = IERC20(token).balanceOf(dispatcher)` (or `address(dispatcher).balance` for native token) and builds a sweep call transferring that **entire balance** to `address(this)` (the Gateway): [1](#0-0) 
3. After the sweep, `received` is measured as the delta on the Gateway's own balance, and if `received <= order.inputs[i].amount`, that observed amount is directly accepted as the order's escrowed input amount, with no verification that the swept funds actually originated from this order's own `predispatch.call` execution: [2](#0-1) 

`dispatcher` is a single shared `CallDispatcher` contract used by every order (`_params.dispatcher`), and it accepts arbitrary native/ERC20 deposits (it has a public `receive()` and any ERC20 can be sent to it directly): [3](#0-2) 

Because the sweep reads the dispatcher's live balance instead of a delta strictly attributable to the current order's `predispatch.call`, any tokens or native currency already sitting in `CallDispatcher` — whether from dust left by a previous order's imperfect sweep, a stuck/failed predispatch execution, or tokens mistakenly sent directly to the well-known `CallDispatcher` address — can be claimed by a subsequent attacker who submits an order for that same token with a minimal/no-op `predispatch.call` and negligible `predispatch.assets`. The attacker's order will be credited with the full swept amount as if it were the attacker's own deposit, funding their own escrow entry that they can later fill/cancel/withdraw through the normal order lifecycle.

### Impact Explanation
This allows an unprivileged caller (an "intent solver"/order placer) to steal tokens or native currency that are sitting in the shared `CallDispatcher` contract but do not belong to them — directly analogous to the Arrakis finding where a malicious vault let an attacker drain tokens accidentally resting in the router. The stolen value is credited into a legitimate escrow entry the attacker fully controls (via `order.user = msg.sender`), so they can subsequently redeem or cancel/refund it through the standard cross-chain settlement path, effectively converting dispatcher-held balance into money they can withdraw. This is concrete theft of protocol/other-party funds reachable from a single unprivileged `placeOrder()` transaction.

### Likelihood Explanation
Likelihood is elevated because `CallDispatcher` is a long-lived, address-known, shared contract reachable by any external transaction (native `receive()` and arbitrary ERC20 transfers), and `placeOrder` is fully permissionless. An attacker only needs the `dispatcher` balance for a token to be non-zero at call time (e.g. dust from a prior order's slippage, a stuck predispatch flow, or a stray transfer) and can construct `order.predispatch.assets`/`order.predispatch.call` to be minimal while `order.inputs` targets that residual balance.

### Recommendation
Track and sweep only the amount actually produced by *this* order's `predispatch.call` execution — e.g., snapshot the dispatcher's balance for each relevant token immediately before transferring `predispatch.assets` (not right before the sweep, after the arbitrary call has already run), and only allow crediting the increase caused by this call, reverting or failing closed if the pre-existing balance is non-zero, rather than sweeping the dispatcher's full live balance.

### Proof of Concept
1. Some balance of `TOKEN` (e.g., dust from a previous order, or a stray transfer) is left sitting in the singleton `CallDispatcher` contract.
2. Attacker calls `placeOrder` with:
   - `order.predispatch.assets` = a single trivial asset (e.g., 1 wei of any token) to satisfy `assets.length > 0`.
   - `order.predispatch.call` = ABI-encoding of an empty `Call[]` (satisfies `call.length > 0`, executes nothing).
   - `order.inputs[i]` = `{ token: TOKEN, amount: <balance already sitting in dispatcher> }`.
3. `placeOrder` executes the predispatch branch: transfers the attacker's trivial asset to `dispatcher`, dispatches a no-op call, then reads `IERC20(TOKEN).balanceOf(dispatcher)` — which equals the residual balance — and sweeps it entirely to the Gateway, crediting `order.inputs[i].amount` as fully satisfied.
4. Attacker's order is now escrowed with `TOKEN` funds they never actually contributed; they can fill/cancel to redeem this value through the normal order flow. [4](#0-3)

### Citations

**File:** evm/src/apps/IntentGatewayV2.sol (L235-330)
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
        } else {
            for (uint256 i; i < inputsLen;) {
                if (order.inputs[i].amount == 0) revert InvalidInput();
                address token = address(uint160(uint256(order.inputs[i].token)));
                if (token == address(0)) {
                    if (msgValue < order.inputs[i].amount) revert InsufficientNativeToken();
                    msgValue -= order.inputs[i].amount;
                } else {
                    uint256 balBefore = IERC20(token).balanceOf(address(this));
                    IERC20(token).safeTransferFrom(msg.sender, address(this), order.inputs[i].amount);
                    order.inputs[i].amount = IERC20(token).balanceOf(address(this)) - balBefore;
                }

                unchecked {
                    ++i;
                }
            }
        }

```

**File:** evm/src/utils/CallDispatcher.sol (L36-60)
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
```
