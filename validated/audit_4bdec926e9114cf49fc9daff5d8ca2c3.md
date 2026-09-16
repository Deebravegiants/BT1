## Title
Zero-amount inputs bypass validation in the Tron `IntentGatewayV2.placeOrder` predispatch path, allowing user funds swept from the CallDispatcher to be lost as unaccounted "dust" instead of being escrowed - ([File: evm/tron/contracts/apps/IntentGatewayV2.sol])

### Summary
The Tron `IntentGatewayV2.placeOrder` function fails to validate that `order.inputs[i].amount != 0` in the predispatch-call code path, unlike the equivalent (and more recent) main EVM `IntentGatewayV2.placeOrder`, which explicitly reverts on zero-amount inputs at multiple points. This mirrors the reported "limit order with amount_in = 0" bug class: an order can be posted whose declared input amount is 0 while real user funds have actually been moved into the `CallDispatcher` via `predispatch.assets` and any predispatch call output. Because the escrow accounting credits only `order.inputs[i].amount` (0) while the sweep step still pulls the dispatcher's *entire* balance of that token into the gateway and logs the rest solely as `DustCollected`, the user's real deposited value is never credited to their own order and cannot be reclaimed via `cancelOrder`/redeem.

### Finding Description
In `evm/tron/contracts/apps/IntentGatewayV2.sol`, `placeOrder` only checks `order.inputs.length == 0` at the top: [1](#0-0) 

When computing `reducedInputs` for the protocol fee deduction, there is no check that `originalAmount != 0`: [2](#0-1) 

In the predispatch branch, predispatch assets are transferred from `msg.sender` to the `CallDispatcher` and an arbitrary call is executed (e.g., a swap), with no zero-amount check on `order.predispatch.assets[i].amount`: [3](#0-2) 

Then the resulting token balance sitting on the dispatcher is swept back to the gateway. `requiredAmount` is taken directly from `order.inputs[i].amount` without any zero check, and the *whole* dispatcher balance is swept in every case: [4](#0-3) 

If `requiredAmount == 0`, `balance < requiredAmount` is never true (so no revert protects the caller), the full swept `balance` is transferred to the gateway, `dust = balance - 0 = balance` is emitted as `DustCollected`, and only `reducedInputs[i].amount` (also 0, since `originalAmount` was 0) is credited to `_orders[commitment][token]`: [5](#0-4) 

By contrast, the more recent main EVM `IntentGatewayV2.sol` closes exactly this gap with explicit `if (amount == 0) revert InvalidInput();` / `if (order.inputs[i].amount == 0) revert InvalidInput();` checks in the analogous predispatch-assets and predispatch-inputs loops: [6](#0-5) 
and the reducedInputs computation: [7](#0-6) 

The Tron deployment lacks these guards entirely in the predispatch branch, so it is reachable by any unprivileged caller of `placeOrder`.

### Impact Explanation
A user who supplies real value through `predispatch.assets` (transferred from their own wallet to the `CallDispatcher` and converted via the predispatch call, e.g., a token swap) but sets `order.inputs[i].amount = 0` for the resulting token has that entire converted balance swept into the gateway contract and irrevocably logged as `DustCollected` (protocol dust) rather than escrowed under their order's commitment. Since `_orders[commitment][token]` is only credited with the (zero) reduced amount, the user cannot recover these funds through `cancelOrder`/withdrawal — the funds are permanently lost to the user and effectively become unaccounted protocol dust. This is a concrete loss/freezing of user funds reachable from a single `placeOrder` transaction, matching the High-severity bug class in the source report.

### Likelihood Explanation
Likelihood is moderate: it does not require a malicious counterparty, only a caller (the order-placing user or a client/SDK bug) supplying a zero `amount` for one of the `order.inputs` entries in the predispatch path, which the contract does not reject. Given the ecosystem has already added the missing checks in the main EVM gateway, this is a known input-validation gap that was fixed in one branch but left present in the Tron branch, increasing the realistic chance it gets triggered by a client-side integration mistake.

### Recommendation
Add the same `if (amount == 0) revert InvalidInput();` guards to `evm/tron/contracts/apps/IntentGatewayV2.sol::placeOrder` that already exist in `evm/src/apps/IntentGatewayV2.sol`: validate `order.predispatch.assets[i].amount != 0`, `order.inputs[i].amount != 0` in the reducedInputs computation, and `order.inputs[i].amount != 0` in both the predispatch sweep loop and the direct-transfer (`else`) loop, so a zero-amount input can never be committed to an order or silently converted into unaccounted dust.

### Proof of Concept
1. User approves `USDC` to the Tron `IntentGatewayV2` and calls `placeOrder` with:
   - `predispatch.assets = [{token: USDC, amount: 1000e6}]`, `predispatch.call` = a swap of 1000 USDC → WETH on the `CallDispatcher`.
   - `inputs = [{token: WETH, amount: 0}]` (the declared/expected input amount is set to 0, whether by a buggy client or unintentionally).
2. `placeOrder` executes: 1000 USDC leaves the user's wallet into the `CallDispatcher`, is swapped to WETH.
3. In the sweep loop, `requiredAmount = 0`; `balance` (the swapped WETH) is fully transferred to the gateway; `dust = balance - 0 = balance` is emitted via `DustCollected`; `_orders[commitment][WETH] += reducedInputs[0].amount` credits 0.
4. The order commitment now shows 0 escrowed WETH even though the gateway actually holds the full swapped WETH balance. The user cannot cancel/withdraw this WETH since `_orders[commitment][WETH] == 0`; the funds are permanently unrecoverable by the user and sit as protocol "dust."

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L338-346)
```text
    function placeOrder(Order memory order, bytes32 graffiti) public payable {
        // Validate that order has inputs
        if (order.inputs.length == 0) revert InvalidInput();

        address hostAddr = host();
        // fill out the order preludes
        order.user = bytes32(uint256(uint160(msg.sender)));
        order.source = IDispatcher(hostAddr).host();
        order.nonce = _nonce++;
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L359-374)
```text
        if (protocolFeeBps > 0) {
            reducedInputs = new TokenInfo[](inputsLen);
            for (uint256 i; i < inputsLen;) {
                uint256 originalAmount = order.inputs[i].amount;
                uint256 protocolFee = (originalAmount * protocolFeeBps) / 10_000;
                uint256 reducedAmount = originalAmount - protocolFee;
                address token = address(uint160(uint256(order.inputs[i].token)));

                // Emit DustCollected for protocol fee if non-zero
                if (protocolFee > 0) emit DustCollected(token, protocolFee);

                reducedInputs[i] = TokenInfo({token: order.inputs[i].token, amount: reducedAmount});
                unchecked {
                    ++i;
                }
            }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L392-414)
```text
            // Transfer all predispatch assets to the call dispatcher
            uint256 assetsLen = order.predispatch.assets.length;
            for (uint256 i; i < assetsLen;) {
                address token = address(uint160(uint256(order.predispatch.assets[i].token)));
                uint256 amount = order.predispatch.assets[i].amount;

                if (token == address(0)) {
                    if (amount > msgValue) revert InsufficientNativeToken();
                    msgValue -= amount;

                    (bool sent,) = dispatcher.call{value: amount}("");
                    if (!sent) revert InsufficientNativeToken();
                } else {
                    IERC20(token).safeTransferFrom(msg.sender, dispatcher, amount);
                }

                unchecked {
                    ++i;
                }
            }

            // Execute the call dispatcher with predispatch call
            ICallDispatcher(dispatcher).dispatch(order.predispatch.call);
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L417-446)
```text
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

**File:** evm/src/apps/IntentGatewayV2.sol (L238-266)
```text
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
```

**File:** evm/src/apps/IntentGatewayV2.sol (L340-344)
```text
        if (protocolFeeBps > 0) {
            reducedInputs = new TokenInfo[](inputsLen);
            for (uint256 i; i < inputsLen;) {
                uint256 originalAmount = order.inputs[i].amount;
                if (originalAmount == 0) revert InvalidInput();
```
