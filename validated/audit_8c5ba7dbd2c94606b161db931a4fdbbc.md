### Title
Fee-on-transfer/deflationary tokens can permanently lock escrowed funds in the Tron `IntentGatewayV2` - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The Tron variant of `IntentGatewayV2` credits order escrow with the *nominal* (requested) input amount instead of the amount actually received by the contract. For a fee-on-transfer/deflationary ERC20 used as an order input, the contract's real token balance will be less than what is recorded in `_orders[commitment][token]`. When the order is later redeemed, refunded, or cancelled, `withdraw()` attempts to transfer the recorded (inflated) amount, which reverts because the contract does not hold that much of the token — permanently freezing the user's/solver's funds for that order.

### Finding Description
In `placeOrder()` (non-predispatch branch), tokens are pulled with a plain `safeTransferFrom` and the escrow is credited with the fee-reduced *requested* amount, without ever checking the contract's actual balance change: [1](#0-0) 

Contrast this with the non-Tron `IntentGatewayV2.sol`, which explicitly measures `balBefore`/`balanceOf(address(this))` after the transfer and mutates `order.inputs[i].amount` to the *actual* received amount before it is used to compute the commitment and credit escrow: [2](#0-1) 

The predispatch branch of the Tron contract has the same defect: it sizes the sweep-back transfer using the dispatcher's actual balance, but still credits escrow with the nominal `reducedInputs[i].amount` rather than what `address(this)` actually received (which, for a fee-on-transfer token, is again lower due to the extra transfer): [3](#0-2) 

Later, when the order is settled — via `RedeemEscrow`, `RefundEscrow` (both routed through `onAccept`), or the GET-response cancellation path (`onGetResponse`) — `withdraw()` uses the amount from the `WithdrawalRequest` (matching the inflated escrow bookkeeping) and performs a raw `token.call` transfer that must fully succeed or the whole withdrawal reverts: [4](#0-3) [5](#0-4) 

Because the contract's real balance of the fee-on-transfer token is smaller than the recorded escrow amount, this transfer call fails and `withdraw()` reverts entirely — for the fill/redeem path, the refund/cancel path, and the destination-chain cancellation path alike, since they all funnel through the same `withdraw()` function.

### Impact Explanation
This is a direct, permanent freezing-of-funds bug reachable by any unprivileged user placing an order with a deflationary/fee-on-transfer token as an input on the Tron `IntentGatewayV2` deployment. Once escrowed, the order can never be successfully settled or refunded: the solver cannot redeem the fill, and the user cannot cancel/refund, because every code path that releases the escrow attempts to transfer more tokens than the contract holds and reverts. This matches the class of bug flagged in the source report (Teller's collateral-withdrawal issue): stale/mis-tracked deposited amounts causing later withdrawal reverts and asset lock-up.

### Likelihood Explanation
Likelihood is moderate-to-high wherever the Tron `IntentGatewayV2` is deployed with support for arbitrary ERC20 inputs, since fee-on-transfer and rebasing/deflationary tokens are common on EVM-compatible chains (including Tron's TRC20 ecosystem) and nothing in `placeOrder` restricts input tokens to standard, non-fee ERC20s. Notably, the primary (non-Tron) `IntentGatewayV2.sol` already contains explicit before/after balance tracking and dedicated fee-on-transfer regression tests (`testPlaceOrder_FeeOnTransferToken_EscrowMatchesReceived`, `testPlaceAndFill_FeeOnTransferToken_RoundTrip`, `testPlaceOrder_FeeOnTransferToken_Predispatch`), confirming the team is aware of and has fixed this exact bug class elsewhere — but the fix was not carried over to the Tron variant, and no equivalent tests exist for `evm/tron/contracts/apps/IntentGatewayV2.sol`.

### Recommendation
Mirror the fix already present in `evm/src/apps/IntentGatewayV2.sol`: measure the gateway's/dispatcher's token balance immediately before and after each `safeTransferFrom`/sweep call, mutate `order.inputs[i].amount` (and thus the fee-reduced amount credited to `_orders`) to the actual amount received, and compute the order commitment over these actual amounts. This ensures `_orders[commitment][token]` never exceeds the contract's real balance, so `withdraw()` can always fulfill redemptions, refunds, and cancellations for fee-on-transfer/deflationary tokens.

### Proof of Concept
1. Deploy `IntentGatewayV2` (Tron variant) and a deflationary ERC20 `FOT` that takes, e.g., a 1% fee on every `transfer`/`transferFrom`.
2. User calls `placeOrder` with `order.inputs[0] = {token: FOT, amount: 1000e18}` and approves the gateway for `1000e18`.
3. Inside `placeOrder`, `safeTransferFrom(user, address(this), 1000e18)` executes; the gateway's actual `FOT` balance only increases by `990e18` (1% fee burned/redirected), but `_orders[commitment][FOT]` is credited with `reducedInputs[0].amount` derived from the full `1000e18` (minus any protocol fee), i.e., an amount greater than `990e18`.
4. A solver fills the order and the gateway dispatches a `RedeemEscrow` request; when `onAccept`/`withdraw()` runs, it attempts `FOT.call(transfer(solver, escrowedAmount))` where `escrowedAmount > actual balance held` — this transfer returns `false`/reverts, and `withdraw()` reverts with `TransferFailed`.
5. The same failure occurs if the user instead tries to cancel and refund via `onGetResponse` → `withdraw(body, true)`, since it uses the identical inflated `body.tokens[i].amount`. The escrowed `FOT` is now permanently stuck — no code path can successfully call `withdraw()` for this commitment.

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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L738-743)
```text
    function onGetResponse(IncomingGetResponse calldata incoming) external override onlyHost {
        if (incoming.response.values[0].value.length != 0) revert Filled();

        WithdrawalRequest memory body = abi.decode(incoming.response.request.context, (WithdrawalRequest));
        withdraw(body, true);
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
