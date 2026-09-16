### Title
Tron `IntentGatewayV2.placeOrder` credits escrow with nominal amounts instead of actual received balance, breaking accounting for fee-on-transfer tokens - (File: evm/tron/contracts/apps/IntentGatewayV2.sol)

### Summary
The Tron variant of `IntentGatewayV2.placeOrder` computes the escrowed amount from the user-supplied `order.inputs[i].amount` (minus only the protocol fee), and never measures the actual token balance received by the contract via `safeTransferFrom`. For fee-on-transfer/deflationary ERC20 tokens, the contract will receive less than `order.inputs[i].amount`, yet `_orders[commitment][token]` is credited with the full (fee-reduced-only) nominal amount, over-crediting the escrow relative to the tokens actually held.

### Finding Description
In the canonical EVM `IntentGatewayV2.sol` (`evm/src/apps/IntentGatewayV2.sol`), `placeOrder` was hardened against fee-on-transfer tokens: it snapshots the contract's balance before `safeTransferFrom` and mutates `order.inputs[i].amount` to the actual delta received: [1](#0-0) 

The Tron contract (`evm/tron/contracts/apps/IntentGatewayV2.sol`) does not implement this pattern. It computes `reducedInputs` (and the commitment) purely from `order.inputs[i].amount` reduced only by the protocol fee percentage: [2](#0-1) 

It then performs the token transfer via `safeTransferFrom(msg.sender, address(this), order.inputs[i].amount)` (using the *nominal* amount, not a balance-based measurement), and unconditionally credits the escrow mapping with `reducedInputs[i].amount`: [3](#0-2) 

The same nominal-amount crediting also occurs on the predispatch path, where `_orders[commitment][token] += reducedInputs[i].amount` uses the pre-fee nominal amount rather than the swept balance actually captured: [4](#0-3) 

For a fee-on-transfer token, `IERC20(token).safeTransferFrom(msg.sender, address(this), order.inputs[i].amount)` will deliver `order.inputs[i].amount - fee` tokens to the gateway, but the escrow bookkeeping (`_orders[commitment][token]`) still records `order.inputs[i].amount` (minus only protocol fee, not the ERC20 transfer fee). This mirrors exactly the referenced Allo `_fundPool()` bug class: the internal accounting variable overstates the actual token balance held by the contract.

### Impact Explanation
Because escrow accounting is inflated relative to actual token holdings, when the order is later filled/redeemed (via `RedeemEscrow`/withdrawal flow that pays out based on `_orders[commitment][token]`), the contract will attempt to transfer out more tokens than it physically holds for that token. This causes:
- Reverting withdrawals/fills for orders funded with fee-on-transfer tokens (denial of service), and/or
- Insolvency across the pool of escrowed balances for that token — other unrelated orders' redemptions can fail or be starved because the ledger no longer matches the real balance, permanently freezing/stranding user or solver funds.

This is a concrete freezing-of-funds / accounting-insolvency vulnerability reachable by any user submitting a single `placeOrder` transaction with a fee-on-transfer ERC20 as input — no privileged role required.

### Likelihood Explanation
Likelihood is Medium: it requires the input token to be a fee-on-transfer/deflationary ERC20 (not all tokens exhibit this behavior), but the protocol elsewhere (main EVM `IntentGatewayV2.sol` and its test suite, e.g. `evm/tests/foundry/IntentGatewayV2SameChainTest.sol`) explicitly acknowledges and tests support for such tokens, showing this is an intended supported token class for the protocol as a whole, and the Tron deployment simply lacks the corresponding fix.

### Recommendation
Apply the same balance-snapshot pattern used in `evm/src/apps/IntentGatewayV2.sol` to the Tron contract: record `IERC20(token).balanceOf(address(this))` (or the dispatcher's balance in the predispatch sweep path) before and after each transfer, use the measured delta as `order.inputs[i].amount` before computing `reducedInputs`/commitment/escrow, exactly mirroring lines 312-329 and 260-311 of the main contract.

### Proof of Concept
1. Deploy the Tron `IntentGatewayV2` and a fee-on-transfer ERC20 token (e.g., 1% fee) as in `FeeOnTransferToken` from `evm/tests/foundry/IntentGatewayV2SameChainTest.sol` (lines 2689-2735).
2. User calls `placeOrder` with `order.inputs[0] = {token: FOT, amount: 1000e18}`, `protocolFeeBps = 0` for simplicity.
3. `safeTransferFrom(user, gateway, 1000e18)` delivers only `990e18` to the gateway (1% fee burned/redirected) — contract's actual FOT balance is `990e18`.
4. `reducedInputs[0].amount` computed from nominal `1000e18` (since no protocol fee) is `1000e18`, and `_orders[commitment][FOT] = 1000e18` is credited — 10e18 more than the contract actually holds.
5. When the order is later filled and the escrow is redeemed (`RedeemEscrow`/withdrawal transferring `_orders[commitment][FOT]` = `1000e18` to the beneficiary), the transfer will fail or drain FOT balance belonging to other escrowed orders, since the gateway only has `990e18` on hand — demonstrating the insolvency/DoS.

### Citations

**File:** evm/src/apps/IntentGatewayV2.sol (L312-329)
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

                unchecked {
                    ++i;
                }
            }
        }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L359-385)
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

            // Temporarily swap inputs to calculate commitment with reduced amounts
            TokenInfo[] memory originalInputs = order.inputs;
            order.inputs = reducedInputs;
            commitment = keccak256(abi.encode(order));
            order.inputs = originalInputs;
        } else {
            // No protocol fees, use order.inputs directly
            reducedInputs = order.inputs;
            commitment = keccak256(abi.encode(order));
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
