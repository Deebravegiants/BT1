### Title
Escrow accounting in Tron `IntentGatewayV2.placeOrder` credits requested input amount instead of actual tokens received, causing insolvent escrow and frozen withdrawals for fee-on-transfer tokens - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The Tron copy of `IntentGatewayV2.placeOrder` computes the escrow credit (`_orders[commitment][token]`) from the *requested* `order.inputs[i].amount` (reduced only by the protocol fee), but never verifies that this is the amount the contract actually received from `safeTransferFrom`. For fee-on-transfer or otherwise lossy ERC20 tokens, the contract will hold strictly less than what it records as escrowed, mirroring the root cause in the referenced Sherlock report: a piece of accounting state is updated using the *intended* amount rather than the *actual* amount moved by an external call whose output can diverge from its input.

### Finding Description
In `evm/tron/contracts/apps/IntentGatewayV2.sol::placeOrder`, the non-predispatch escrow path is: [1](#0-0) 

For each input token, `IERC20(token).safeTransferFrom(msg.sender, address(this), order.inputs[i].amount)` is executed, then `_orders[commitment][token] += reducedInputs[i].amount` is credited using the *pre-transfer, fee-reduced requested amount* — not the delta in the contract's actual token balance. `reducedInputs` itself is derived purely from `order.inputs[i].amount` minus the protocol fee, computed before any transfer occurs: [2](#0-1) 

The predispatch branch has the same defect: `dust` is computed from `balance - requiredAmount` (an overpayment check only), but the actual escrow credit still uses `reducedInputs[i].amount`, the pre-computed requested value, not the measured balance: [3](#0-2) 

This is the exact analog of the reported bug class: an accounting variable (`currentStakeLimit` in the original report, `_orders[commitment][token]` here) is updated using the *input* amount to an external operation, while the operation's *actual effect* (`_stake()`'s return value` there, the ERC20 balance delta here) can be smaller. The current production `evm/src/apps/IntentGatewayV2.sol` was patched to measure `balanceOf` before/after transfer and mutate `order.inputs[i].amount` to the actually received amount before crediting escrow: [4](#0-3) 

but the Tron contract at `evm/tron/contracts/apps/IntentGatewayV2.sol` does not carry this fix, and continues crediting escrow with the unverified requested amount.

### Impact Explanation
Because `_orders[commitment][token]` is a shared per-token liability ledger backed by the pooled ERC20 balance of the contract, over-crediting one order's escrow (via a fee-on-transfer or otherwise lossy token) makes the aggregate recorded liabilities exceed the contract's actual token balance. When `withdraw()` later attempts to pay out escrowed tokens for *any* order in that token (including unrelated, honestly-funded orders), the raw `token.call(transfer(...))` can fail once the pool is insolvent, reverting with `TransferFailed()`: [5](#0-4) 

This permanently freezes legitimate users'/solvers' escrowed funds for that token, since the contract can no longer satisfy all outstanding `_orders` balances. This is a Medium/High severity finding: permanent freezing of user/solver funds due to unsound escrow-accounting invariant, triggerable by any user who places an order using a fee-on-transfer (or non-standard, lossy) ERC20 as an input asset — a single `placeOrder` transaction from an unprivileged caller.

### Likelihood Explanation
Likelihood depends on whether the deployed input-token allowlist for the Tron gateway includes any token with transfer fees, rebasing, or other loss-on-transfer behavior. Given `IntentGatewayV2` is designed to be generic and accepts arbitrary ERC20 `TokenInfo.token` addresses supplied by users in `order.inputs`, and fee-on-transfer tokens are common on Tron/EVM ecosystems, this is realistically reachable without any privileged action — it only requires one `placeOrder` call with such a token.

### Recommendation
Mirror the fix already applied to `evm/src/apps/IntentGatewayV2.sol`: measure the contract's token balance immediately before and after each `safeTransferFrom` (or dispatcher sweep) and use the measured delta — not the requested `order.inputs[i].amount` — both for the protocol-fee reduction/commitment computation and for the `_orders[commitment][token]` credit. Apply the same balance-delta measurement to the predispatch/dispatcher sweep branch so `dust` and escrow amounts are both derived from actual balances, not intended amounts.

### Proof of Concept
1. Deploy a fee-on-transfer ERC20 (e.g., 1% fee) and register it as an allowed input token for the Tron `IntentGatewayV2`.
2. User calls `placeOrder` with `order.inputs[0] = {token: FOT, amount: 1000e18}`, and `protocolFeeBps == 0` for simplicity.
3. `safeTransferFrom(user, address(this), 1000e18)` executes; contract actually receives only `990e18` (1% fee burned/retained by token).
4. `reducedInputs[0].amount` is still `1000e18` (no protocol fee to subtract), and `_orders[commitment][FOT] += 1000e18` is credited — 10e18 more than the contract actually holds.
5. Repeat with other users/orders using the same FOT token; the ledger total for `FOT` across all commitments now exceeds `FOT.balanceOf(address(gateway))`.
6. When `withdraw()` is eventually called for any of these orders (via fill settlement or cancellation refund), the aggregate shortfall causes some `token.call(transfer(...))` to fail, permanently freezing the affected user's/solver's escrowed `FOT` tokens.

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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L702-710)
```text
            if (token == address(0)) {
                (bool sent,) = beneficiary.call{value: amount}("");
                if (!sent) revert InsufficientNativeToken();
            } else {
                (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
                if (!success) revert TransferFailed();
            }

            _orders[body.commitment][token] -= amount;
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
