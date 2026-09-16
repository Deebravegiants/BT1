## Analog Found

### Title
Fee-on-transfer tokens not handled in Tron `IntentGatewayV2.placeOrder`, causing escrow over-crediting and stuck/undeliverable redemptions - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The Tron variant of `IntentGatewayV2.placeOrder` credits escrow accounting using the user-specified gross input amount (minus protocol fee), but never verifies how many tokens the contract actually received via `safeTransferFrom`. For fee-on-transfer (FOT) ERC20s, the contract's real token balance increase is less than the amount credited to `_orders[commitment][token]`, creating an accounting/balance mismatch identical in root cause to the reported UToken bug ("fee-on-transfer tokens not handled consistently... difference of balance before/after not checked").

### Finding Description
In the escrow branch of `placeOrder` (no predispatch call), the contract does: [1](#0-0) 

```solidity
} else {
    for (uint256 i; i < inputsLen;) {
        if (order.inputs[i].amount == 0) revert InvalidInput();
        address token = address(uint160(uint256(order.inputs[i].token)));
        if (token == address(0)) {
            if (msgValue < order.inputs[i].amount) revert InsufficientNativeToken();
            msgValue -= order.inputs[i].amount;
        } else {
            IERC20(token).safeTransferFrom(msg.sender, address(this), order.inputs[i].amount);
        }
        // Store reduced amount (after protocol fees) in escrow
        _orders[commitment][token] += reducedInputs[i].amount;
        ...
```

`reducedInputs[i].amount` is derived purely from `order.inputs[i].amount` (the user-specified gross amount) minus the protocol fee — it is never adjusted for the actual token balance received: [2](#0-1) 

No `balanceOf(address(this))` before/after check exists in this path (unlike the EVM `src` version), so if `token` is a fee-on-transfer ERC20, the escrow ledger `_orders[commitment][token]` is inflated above what the contract actually holds.

This contrasts with the canonical, fixed EVM implementation of the same contract, which explicitly measures the balance delta to stay consistent with actual holdings: [3](#0-2) 

The same over-crediting also applies to the predispatch branch, where `dust` is computed correctly (line 437) but the escrow is still credited with `reducedInputs[i].amount` derived from the pre-transfer amount rather than actual balance received, at: [4](#0-3) 

Downstream, `withdraw()` performs a raw `token.call` transfer of the full recorded amount without any balance guard: [5](#0-4) 

### Impact Explanation
Because `_orders[commitment][token]` is a shared accounting ledger for a given `token` address across all orders (not a segregated balance), inflating one order's credited amount for an FOT token means the contract's real balance of that token is less than the sum of all outstanding escrow claims. This can result in:
- Permanent freezing of funds: `withdraw()` (invoked from `onAccept` for `RedeemEscrow`/`RefundEscrow`, or from `onGetResponse` for a cancellation) reverts with `TransferFailed` when the actual balance is insufficient to cover the recorded amount, making that redemption impossible.
- Fund loss to other users: if the shortfall is not enough to fully block a transfer, an earlier or unrelated order sharing the same FOT token can have its own escrow depleted for the benefit of a different order's beneficiary, since the token transfer draws from the pooled contract balance, not from a segregated per-order balance.

This satisfies the "permanent freezing of funds" / "unsound state commitment" bar for Medium+ severity.

### Likelihood Explanation
Any user can call `placeOrder` with an arbitrary ERC20 `token` address as input — there is no allow-list restricting inputs to non-FOT tokens on the Tron deployment. Any fee-on-transfer token (a well-known and reasonably common token category) placed as an order input on this Tron contract deterministically triggers the mismatch on every single order placement, making this readily reachable by an unprivileged user placing an order (a single transaction), not requiring any privileged role.

### Recommendation
Apply the same balance-before/balance-after pattern used in the EVM `src/apps/IntentGatewayV2.sol` implementation to the Tron variant: measure `IERC20(token).balanceOf(address(this))` immediately before and after each `safeTransferFrom` call (both in the direct-escrow branch and in the predispatch sweep-back branch), and use the measured delta — not the user-supplied nominal amount — when computing `reducedInputs`/the commitment hash and when crediting `_orders[commitment][token]`.

### Proof of Concept
1. Deploy a 1%-fee ERC20 (`FeeOnTransferToken`, feeBps=100) as done in the existing test suite for the EVM `src` gateway (`evm/tests/foundry/IntentGatewayV2SameChainTest.sol`, `FeeOnTransferToken` contract, lines 2690-2735).
2. User calls `IntentGatewayV2(Tron).placeOrder` with `order.inputs[0] = {token: FOT, amount: 1000e18}`, no protocol fee, no predispatch.
3. `safeTransferFrom(msg.sender, address(this), 1000e18)` results in the gateway actually receiving only `990e18` (1% fee burned/retained by token), while `_orders[commitment][FOT] += reducedInputs[0].amount` credits the escrow with the full `1000e18` (since `protocolFeeBps == 0`, `reducedInputs = order.inputs`).
4. Gateway `IERC20(FOT).balanceOf(address(this))` is `990e18`, but `_orders[commitment][FOT]` records `1000e18` — a permanent 10e18 shortfall.
5. When `onAccept`/`withdraw` is later invoked to pay out `1000e18` to the beneficiary, the raw `token.call(transfer, beneficiary, 1000e18)` either reverts (`TransferFailed`, freezing this order's funds) or succeeds by draining tokens belonging to other orders sharing the same FOT token, causing accounting insolvency across the ledger.

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
