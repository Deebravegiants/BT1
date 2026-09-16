### Title
Tron `IntentGatewayV2.placeOrder` escrows the nominal input amount instead of the actual fee-on-transfer-adjusted balance received, causing permanent under-collateralization of escrowed orders - (File: evm/tron/contracts/apps/IntentGatewayV2.sol)

### Summary
The Tron variant of the intents contract, `evm/tron/contracts/apps/IntentGatewayV2.sol`, does not measure actual token balances received when escrowing order inputs. It directly credits `_orders[commitment][token]` with the caller-supplied (fee-reduced-only-by-protocol-fee) amount rather than the amount actually transferred into the contract, so fee-on-transfer tokens create an escrow ledger that overstates the contract's real token holdings. This is the same bug class flagged in the Sherlock report against `Allo::_fundPool()`, where an internal accounting variable is incremented by the pre-fee amount instead of the actually-received post-fee amount.

### Finding Description
In `placeOrder`, when there is no predispatch call, tokens are pulled straight from the user with `safeTransferFrom` and the escrow ledger is updated with `reducedInputs[i].amount` — an amount derived purely from the user-declared `order.inputs[i].amount` minus the protocol fee, with no reconciliation against the contract's actual token balance before/after the transfer: [1](#0-0) 

Compare this to the mainline EVM `IntentGatewayV2.sol`, which explicitly measures `balBefore`/`balanceOf` deltas and mutates `order.inputs[i].amount` to the actually-received value before computing the commitment/escrow, precisely to defend against fee-on-transfer tokens: [2](#0-1) 

The Tron contract's predispatch branch does perform a `balanceOf(dispatcher)` check before sweeping funds back to the gateway, but even there it escrows `reducedInputs[i].amount` (based on the originally-requested amount) rather than the amount the gateway itself actually received after the sweep transfer (which itself can incur another fee-on-transfer haircut): [3](#0-2) 

Because `_orders[commitment][token]` is the value later paid out on `withdraw()` (used both for `RedeemEscrow`/fill payouts and `RefundEscrow`/cancellations), any inflation of this ledger value relative to the token balance actually held by the contract directly translates into insolvency of the escrow accounting: [4](#0-3) 

### Impact Explanation
When a user places an order with a fee-on-transfer token, the contract receives strictly less than `order.inputs[i].amount` (minus protocol fee), yet credits the escrow ledger with the full nominal (pre-transfer-fee) amount. This causes the sum of all `_orders[commitment][token]` entries for that token to exceed the actual token balance held by the `IntentGatewayV2` contract. Since `withdraw()` pays out based on the ledger value, this can permanently freeze funds for other legitimate order beneficiaries/solvers: once enough escrow entries are redeemed against the shared, undercollateralized token balance, later legitimate `withdraw()` calls for other still-outstanding orders (fills or cancellation refunds) will fail due to insufficient token balance, since the contract does not hold enough of the token to honor its own accounting. This is a concrete freezing-of-funds condition reachable by any unprivileged user simply calling `placeOrder` with a fee-on-transfer token, matching the severity bar (permanent freezing of funds due to unsound accounting).

### Likelihood Explanation
Likelihood is high for any deployment of this Tron contract on networks with fee-on-transfer tokens: the vulnerable code path (`placeOrder` without predispatch) is the default, most common flow, requires only a single `placeOrder` transaction from any unprivileged caller, and there is no validation rejecting fee-on-transfer tokens. The mainline EVM contract has already been hardened against exactly this issue (as shown by the `balBefore`/`balanceOf` delta pattern and the dedicated `FeeOnTransferToken` test suite), confirming this is a known, previously-fixed bug class that was not carried over to the Tron fork.

### Recommendation
Mirror the fix already present in `evm/src/apps/IntentGatewayV2.sol`: before crediting `_orders[commitment][token]`, measure `balanceOf(address(this))` before and after each `safeTransferFrom` (and similarly reconcile the predispatch sweep-back transfer), and use the actual delta — not the nominal/requested amount — both for computing `reducedInputs` (protocol fee base) and for the value stored into `_orders[commitment][token]`.

### Proof of Concept
1. Deploy the Tron `IntentGatewayV2` and configure an order whose input token is a 1% fee-on-transfer ERC20 (e.g., the `FeeOnTransferToken` test helper already used in the EVM test suite at `evm/tests/foundry/IntentGatewayV2SameChainTest.sol:2690`).
2. User calls `placeOrder` with `order.inputs[0].amount = 1000e18` for this token, with `_params.protocolFeeBps == 0` for simplicity.
3. `safeTransferFrom(msg.sender, address(this), 1000e18)` executes; due to the 1% fee, the gateway's actual token balance only increases by `990e18`.
4. `_orders[commitment][token] += reducedInputs[i].amount` credits `1000e18` (since `reducedInputs == order.inputs` when there's no protocol fee) — 10e18 more than what the contract actually holds.
5. Repeat with more such orders; the aggregate escrow ledger for that token now exceeds the contract's real balance by the accumulated transfer-fee shortfall.
6. When the last such order's beneficiary/solver calls `withdraw()` (via `onAccept`/`cancelOrder`), the token transfer reverts due to insufficient contract balance, permanently freezing that order's escrowed funds while other, earlier claimants extracted the full nominal amounts.

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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L691-700)
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
