### Title
Fee-on-transfer tokens cause escrow over-crediting and stuck/insolvent orders in the Tron IntentGatewayV2 `placeOrder` - ([File: evm/tron/contracts/apps/IntentGatewayV2.sol])

### Summary
The Tron variant of `IntentGatewayV2.placeOrder` credits escrow (`_orders[commitment][token]`) with the *stated* input amount (minus protocol fee), never verifying how many tokens the contract actually received via `safeTransferFrom`. For deflationary/fee-on-transfer ERC20 tokens, the contract will hold fewer tokens than it has credited to the order, leading to under-collateralized escrow entries that cannot be fully redeemed and, in shared-balance scenarios, can drain funds belonging to other legitimate orders.

### Finding Description
In the non-predispatch branch of `placeOrder`: [1](#0-0) 

the contract calls `IERC20(token).safeTransferFrom(msg.sender, address(this), order.inputs[i].amount)` and then unconditionally credits `_orders[commitment][token] += reducedInputs[i].amount`, where `reducedInputs[i].amount` is derived purely from the user-stated `order.inputs[i].amount` minus the protocol fee — computed *before* any transfer occurs: [2](#0-1) 

If the ERC20 token charges a transfer fee (e.g., USDT-style deflationary tokens), the amount actually received by the gateway is less than `order.inputs[i].amount`, yet the escrow accounting and the commitment hash are computed as if the full amount arrived. This is the same root cause as the referenced Juicebox finding: crediting "amount stated" instead of "amount transferred."

By contrast, the standard EVM `IntentGatewayV2.sol` (`evm/src/apps/IntentGatewayV2.sol`) was hardened against exactly this class of bug — it snapshots balances before/after `safeTransferFrom` and mutates `order.inputs[i].amount` to the actually-received value before computing the commitment and crediting escrow: [3](#0-2) 

The Tron contract's predispatch branch does perform a balance-based check for the sweep from the call dispatcher (`balance = IERC20(token).balanceOf(dispatcher)`), but that check only validates that the dispatcher's balance is not less than the required amount and still credits `reducedInputs[i].amount` (the stated/fee-reduced amount) rather than what the gateway itself received after the second, gateway-side transfer: [4](#0-3) 

Since `balanceOf(address(this))` after the sweep transfer is never captured, a fee-on-transfer token in this path also results in the gateway crediting more escrow than tokens actually held.

### Impact Explanation
Because `_orders[commitment][token]` is a shared token-balance ledger across all orders escrowed in that contract, over-crediting one order's escrow with more than the tokens actually held creates a systemic shortfall in the contract's real token balance versus its accounted liabilities. When `withdraw()` (invoked via `onAccept` for `RedeemEscrow`/`RefundEscrow`, or via `cancelOrder`) attempts to pay out the full credited/stated amount to a solver or to refund the user, the ERC20 `transfer` can revert due to insufficient actual balance — permanently freezing that order's funds. Worse, because token balance is fungible and shared, an early withdrawal made against one commitment can drain from the pool of tokens actually deposited by other users, causing subsequent legitimate withdrawals for unrelated orders to unexpectedly fail (freeze of other users' funds) — a permanent loss/freezing of funds scenario, which is Medium/High severity per Hyperbridge's own fix already applied to the mainline EVM contract for this exact bug class.

### Likelihood Explanation
Likelihood is moderate: it requires a project/deployment of the Tron `IntentGatewayV2` to accept a fee-on-transfer/deflationary ERC20 as an input token. Given Tron hosts several widely-used deflationary/fee tokens (and the same bug class was already identified and fixed for the primary EVM contract, evidenced by the existing test suite in `IntentGatewayV2SameChainTest.sol` specifically targeting fee-on-transfer scenarios), any listing of such a token on the Tron gateway will trigger this immediately and deterministically on every `placeOrder` call using that token — no attacker action beyond a single, permissionless `placeOrder` transaction is required.

### Recommendation
Apply the same fix already implemented in `evm/src/apps/IntentGatewayV2.sol` to the Tron variant: snapshot the contract's token balance immediately before and after each `safeTransferFrom` call in `placeOrder` (both the non-predispatch branch and the post-sweep gateway-side transfer in the predispatch branch), and use the measured delta — not the user-stated `order.inputs[i].amount` — as the basis for computing `reducedInputs`, the commitment hash, and the amount credited to `_orders[commitment][token]`.

### Proof of Concept
1. Deploy a fee-on-transfer ERC20 token (e.g., 1% fee) on the Tron network's `IntentGatewayV2`.
2. User calls `placeOrder` with `order.inputs[0] = {token: FOT, amount: 1000e18}`, approves the gateway for `1000e18`.
3. `safeTransferFrom(msg.sender, address(this), 1000e18)` executes; due to the 1% fee, the gateway only receives `990e18` tokens (see `_transfer` fee-simulation logic used in the existing FOT test at `evm/tests/foundry/IntentGatewayV2SameChainTest.sol:2726-2730`).
4. Despite only holding `990e18`, `_orders[commitment][FOT]` is credited with `reducedInputs[0].amount = 1000e18` (or `1000e18` minus protocol fee if configured) — an amount the contract does not actually hold.
5. When a solver later fills the order and the corresponding `RedeemEscrow` request triggers `withdraw()` for `1000e18` (or the fee-reduced-but-still-overstated amount), the ERC20 `transfer` call reverts because the gateway's actual FOT balance (`990e18`) is insufficient, freezing the order — or, if other unrelated orders hold FOT balance in the same contract, the withdrawal succeeds by consuming tokens belonging to those other orders, causing their later withdrawals to fail instead.

### Citations

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
