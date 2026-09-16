Confirmed: the Tron variant of `IntentGatewayV2.sol` does not implement the fee-on-transfer fix that the mainline EVM `IntentGatewayV2.sol` has. This is the exact same bug class as the reported Sherlock finding — the contract escrows/accounts for the nominal `order.inputs[i].amount` instead of the tokens actually received.

### Title
Tron `IntentGatewayV2.placeOrder` credits escrow with pre-fee amount instead of tokens actually received for fee-on-transfer tokens - (File: evm/tron/contracts/apps/IntentGatewayV2.sol)

### Summary
The Tron deployment of `IntentGatewayV2.sol` still uses the vulnerable pattern flagged in the referenced report: it calls `safeTransferFrom` with the user-specified amount and then credits escrow/commitment accounting with a value derived from that same nominal amount, never checking the gateway's actual token balance delta. This is precisely the bug class already fixed in the primary EVM `IntentGatewayV2.sol` (`evm/src/apps/IntentGatewayV2.sol`), which explicitly measures `balanceOf` before/after transfers to compute `received` amounts for fee-on-transfer tokens.

### Finding Description
In `placeOrder` (no-predispatch branch), the Tron contract does: [1](#0-0) 
It calls `IERC20(token).safeTransferFrom(msg.sender, address(this), order.inputs[i].amount)` and then unconditionally does `_orders[commitment][token] += reducedInputs[i].amount`, where `reducedInputs[i].amount` was computed earlier purely from `order.inputs[i].amount` minus the protocol fee bps: [2](#0-1) 
For a fee-on-transfer (deflationary) ERC-20 input token, the actual amount received by the contract is `order.inputs[i].amount - transferFee`, which is strictly less than the escrow amount that gets credited (`order.inputs[i].amount - protocolFee`). The same pattern (crediting `reducedInputs[i].amount` without checking actual balance received) also exists in the predispatch branch: [3](#0-2) 
This directly contrasts with the corrected mainline implementation, which snapshots `balanceOf` before/after transfer and mutates `order.inputs[i].amount` to the actual `received` delta before computing the commitment and crediting escrow: [4](#0-3) [5](#0-4) 

### Impact Explanation
The `_orders[commitment][token]` mapping on Tron becomes over-credited relative to the tokens actually held by the contract for that token. When a solver later fills the order and the escrow is subsequently released via `withdraw` (called from `onAccept` for `RedeemEscrow`/`RefundEscrow`, or directly for same-chain cancel), the contract will attempt to transfer out more tokens than it actually received for this particular commitment: [6](#0-5) 
Because `_orders` is a per-commitment/per-token accounting ledger shared across all users' escrowed balances in the same contract, an over-credit for one fee-on-transfer order either (a) reverts the withdrawal outright when the contract lacks sufficient token balance (denial of service / stuck funds for the legitimate solver or refund beneficiary), or (b) if the contract holds surplus balance from other users' escrows (e.g., accumulated dust or other orders' tokens), silently pays out using other users' escrowed funds, causing insolvency and fund loss for other order owners once they attempt to withdraw. This is a concrete freezing-of-funds / accounting-insolvency vulnerability reachable by any user placing an order with a fee-on-transfer input token — an unprivileged, single-transaction action (`placeOrder`).

### Likelihood Explanation
Any unprivileged user can trigger this by calling `placeOrder` with a fee-on-transfer/deflationary ERC-20 as an input token; no special privileges or governance action are required, only that such a token be usable as an intent input (which the gateway does not reject). Given IntentGatewayV2 is a general-purpose cross-chain intents mechanism intended to support arbitrary ERC-20 tokens (as evidenced by the extensive fee-on-transfer handling already implemented and tested in the mainline EVM contract), likelihood is high wherever a fee-on-transfer token is or becomes supported on the Tron deployment.

### Recommendation
Apply the same fix already present in `evm/src/apps/IntentGatewayV2.sol` to the Tron variant: before crediting `_orders[commitment][token]`, snapshot `IERC20(token).balanceOf(address(this))` before and after each `safeTransferFrom`, use the actual received delta (not the nominal `order.inputs[i].amount`) to compute `reducedInputs`/commitment, and credit escrow with the fee-reduced actual-received amount, mirroring the mainline logic at `evm/src/apps/IntentGatewayV2.sol` lines 312-373.

### Proof of Concept
1. Deploy a fee-on-transfer ERC20 (e.g., 1% fee, as modeled in `FeeOnTransferToken` used in the mainline test suite: `evm/tests/foundry/IntentGatewayV2SameChainTest.sol` lines 2696-2735).
2. User calls `placeOrder` on the Tron `IntentGatewayV2` with `order.inputs[0] = {token: fotToken, amount: 1000e18}`, no predispatch.
3. `safeTransferFrom(msg.sender, address(this), 1000e18)` executes; contract actually receives `990e18` (1% fee burned/redirected).
4. `_orders[commitment][fotToken]` is nonetheless credited with `reducedInputs[0].amount` computed from `1000e18` minus protocol fee (e.g., `997e18` if protocol fee is 30bps), i.e., more than the `990e18` actually held.
5. When the order is later filled/redeemed and `withdraw` attempts to transfer `997e18` to the beneficiary, either the transfer reverts (insufficient contract balance) if no other escrowed tokens of that type exist, or it succeeds by consuming another user's escrowed balance of the same token, breaking that user's later withdrawal.

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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L450-468)
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
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L691-714)
```text
    function withdraw(WithdrawalRequest memory body, bool isRefund) internal {
        address beneficiary = address(uint160(uint256(body.beneficiary)));
        _filled[body.commitment] = beneficiary;

        // redeem escrowed tokens
        uint256 len = body.tokens.length;
        for (uint256 i; i < len;) {
            address token = address(uint160(uint256(body.tokens[i].token)));
            uint256 amount = body.tokens[i].amount;
            if (_orders[body.commitment][token] == 0) revert UnknownOrder();

            if (token == address(0)) {
                (bool sent,) = beneficiary.call{value: amount}("");
                if (!sent) revert InsufficientNativeToken();
            } else {
                (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
                if (!success) revert TransferFailed();
            }

            _orders[body.commitment][token] -= amount;
            unchecked {
                ++i;
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

**File:** evm/src/apps/IntentGatewayV2.sol (L340-373)
```text
        if (protocolFeeBps > 0) {
            reducedInputs = new TokenInfo[](inputsLen);
            for (uint256 i; i < inputsLen;) {
                uint256 originalAmount = order.inputs[i].amount;
                if (originalAmount == 0) revert InvalidInput();
                uint256 protocolFee = (originalAmount * protocolFeeBps) / 10_000;
                uint256 reducedAmount = originalAmount - protocolFee;
                address token = address(uint160(uint256(order.inputs[i].token)));

                if (protocolFee > 0) emit DustCollected(token, protocolFee);

                reducedInputs[i] = TokenInfo({token: order.inputs[i].token, amount: reducedAmount});
                unchecked {
                    ++i;
                }
            }

            order.inputs = reducedInputs;
        } else {
            reducedInputs = order.inputs;
        }
        commitment = keccak256(abi.encode(order));

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
