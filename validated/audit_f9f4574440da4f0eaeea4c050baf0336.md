### Title
Fee-on-transfer tokens break escrow accounting in `IntentGatewayV2.placeOrder` (Tron variant) - ([File: evm/tron/contracts/apps/IntentGatewayV2.sol])

### Summary
The Tron variant of `IntentGatewayV2.placeOrder` credits the internal escrow ledger `_orders[commitment][token]` with the user-stated order amount (minus protocol fee) instead of the amount the contract actually received from `safeTransferFrom`. For fee-on-transfer (deflationary) ERC20 tokens, the contract receives less than `order.inputs[i].amount`, but the escrow bookkeeping assumes the full stated amount was received, permanently desynchronizing on-chain balances from escrow accounting.

### Finding Description
In the non-predispatch branch of `placeOrder`, tokens are pulled directly via `safeTransferFrom` and the escrow map is incremented by `reducedInputs[i].amount`, which is derived purely from `order.inputs[i].amount` (the amount the user declared, only adjusted for the protocol fee), never from an actual balance measurement: [1](#0-0) 

Compare this with the equivalent logic in the primary EVM `IntentGatewayV2.sol`, which explicitly snapshots the balance before and after the transfer and mutates `order.inputs[i].amount` to the actually-received delta specifically to defend against fee-on-transfer tokens: [2](#0-1) 

That protective pattern (measure-before/measure-after) is absent from the Tron contract's equivalent code path. `reducedInputs[i].amount` is computed at lines 362-364 purely as `originalAmount - protocolFee`, with `originalAmount` taken from user input, not from any balance delta: [3](#0-2) 

The predispatch branch is partially safer (it compares dispatcher balance against `requiredAmount` before sweeping), but it still escrows `reducedInputs[i].amount` — derived from the *stated* order amount — rather than the amount actually swept into the gateway, so if the predispatch-assets transfer itself (line 405, a plain `safeTransferFrom`) or the swept token is fee-on-transfer, the same under-collateralization occurs: [4](#0-3) 

### Impact Explanation
When a fee-on-transfer token is used as an order input, the contract's actual token balance for that order will be less than what `_orders[commitment][token]` claims. Since the escrow mapping is shared/aggregated across orders (`+=`), this inflated bookkeeping over-credits the escrow ledger relative to the real balance held by the gateway. Any filler/solver settlement or refund logic that trusts `_orders[commitment][token]` to represent actual redeemable balance can end up allowed to withdraw more than the contract actually holds, at the expense of other users' legitimately escrowed funds — a fund-insolvency/theft condition reachable by any user placing a single order with a fee-on-transfer token.

### Likelihood Explanation
This is triggerable by any unprivileged user calling `placeOrder` with a fee-on-transfer ERC20 as an order input — no special privileges or governance action required, only picking (or being tricked into filling an order that references) a deflationary token as the `order.inputs[i].token`.

### Recommendation
Mirror the fix already present in `evm/src/apps/IntentGatewayV2.sol`: measure the gateway's/dispatcher's token balance immediately before and after each `safeTransferFrom` (and after predispatch asset transfers/sweeps), and use the actual received delta — not the user-stated `order.inputs[i].amount` — both for the commitment hash and for the `_orders[commitment][token]` escrow credit in the Tron contract.

### Proof of Concept
1. Deploy a fee-on-transfer ERC20 token (e.g. 2% fee) and register it as a valid input token.
2. User calls `placeOrder` with `order.inputs[0] = {token: FOT, amount: 1000}` and no predispatch call, going through the `else` branch at `evm/tron/contracts/apps/IntentGatewayV2.sol:450-469`.
3. `safeTransferFrom(msg.sender, address(this), 1000)` executes, but due to the 2% fee, the gateway's actual balance only increases by 980.
4. `_orders[commitment][token] += reducedInputs[0].amount` credits (up to) 1000 (minus any protocol fee) to the escrow ledger, i.e., more than the 980 tokens actually held.
5. Repeating this with multiple orders/fillers progressively decouples the aggregated `_orders` ledger from the real token balance, allowing later settlement/refund of orders to drain tokens belonging to other users' escrowed balances.

### Citations

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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L450-469)
```text
        } else {
            for (uint256 i; i < inputsLen;) {
                if (order.inputs[i].amount == 0) revert InvalidInput();
                address token = address(uint160(uint256(order.inputs[i].token)));
                if (token == address(0)) {
                    // native token
                    if (msgValue < order.inputs[i].amount) revert InsufficientNativeToken();
                    msgValue -= order.inputs[i].amount;
                } else {
                    IERC20(token).safeTransferFrom(msg.sender, address(this), order.inputs[i].amount);
                }

                // Store reduced amount (after protocol fees) in escrow
                _orders[commitment][token] += reducedInputs[i].amount;

                unchecked {
                    ++i;
                }
            }
        }
```

**File:** evm/src/apps/IntentGatewayV2.sol (L312-323)
```text
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
```
