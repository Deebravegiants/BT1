## Title
Escrow accounting in `IntentGatewayV2.placeOrder` (Tron variant) does not reconcile actual token balance received, permanently freezing escrowed funds for fee-on-transfer/rebasing ERC20 inputs - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The Tron fork of `IntentGatewayV2.placeOrder` credits escrow using the *nominal* order amount (minus protocol fee) rather than the token balance actually received by the contract, while the mainline EVM implementation explicitly measures the actual balance delta to guard against exactly this class of token. When a fee-on-transfer or negative-rebasing ERC20 is used as an order input via the direct (non-predispatch) transfer path, the gateway's internal `_orders[commitment][token]` ledger records more tokens than the contract actually holds, and the later `withdraw()` call reverts on transfer, permanently freezing the escrowed funds — the same root-cause pattern as the referenced Teller `CollateralEscrowV1` finding (stale/overstated internal accounting vs. actual token balance, leading to a stuck withdrawal).

### Finding Description
In the direct-transfer (non-predispatch) branch of `placeOrder`: [1](#0-0) 

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

`reducedInputs[i].amount` is derived purely from the user-supplied `order.inputs[i].amount` minus the protocol-fee percentage — it is never reconciled with the actual ERC20 balance the gateway received from `safeTransferFrom`: [2](#0-1) 

For a fee-on-transfer token, or a rebasing token that has rebased down between transfer and any later read, the actual balance held by the gateway can be **less** than the amount credited to `_orders[commitment][token]`.

Compare this to the mainline (non-Tron) `IntentGatewayV2.sol`, which explicitly snapshots the balance before/after the transfer and mutates `order.inputs[i].amount` to the *actual* received amount before computing `reducedInputs` and crediting escrow: [3](#0-2) 

The Tron variant lacks this reconciliation entirely in the direct-transfer path, so the escrow ledger can overstate what the contract actually holds.

When the order is later filled or cancelled, `withdraw()` unconditionally attempts to transfer the recorded `amount` out to the beneficiary and only afterwards decrements the ledger: [4](#0-3) 

```solidity
function withdraw(WithdrawalRequest memory body, bool isRefund) internal {
    ...
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
```

If the recorded `amount` exceeds the gateway's actual token balance (because the ledger was never reconciled at deposit time), the low-level `token.call(...transfer...)` fails and `withdraw()` reverts with `TransferFailed()`. Because `withdraw` is invoked identically for `RedeemEscrow` (fill settlement) and `RefundEscrow`/`onGetResponse` (cancellation), **every path to release the escrow reverts**, permanently locking the deposited funds — there is no admin sweep or alternate accounting-repair path for this ledger entry.

### Impact Explanation
This is a permanent freezing-of-funds bug reachable by any unprivileged user who places an order via `placeOrder` using a fee-on-transfer or rebasing ERC20 as an input token on the Tron `IntentGatewayV2` deployment. Once escrowed, neither the solver (via fill/`RedeemEscrow`) nor the user (via cancel/`RefundEscrow`) can retrieve the tokens, since `withdraw()` reverts on the insufficient-balance transfer. This satisfies the "permanent freezing of funds" acceptance criterion.

### Likelihood Explanation
Likelihood depends on whether fee-on-transfer/rebasing tokens are permitted as order inputs on the Tron deployment; the contract itself performs no allowlist check restricting input tokens, so any user can construct such an order for any ERC20 address supplied as `order.inputs[i].token`. The mainline EVM contract's test suite (`IntentGatewayV2Test.sol`, `IntentGatewayV2SameChainTest.sol`) explicitly exercises fee-on-transfer scenarios, confirming this is an anticipated real-world token category for this protocol, and the Tron variant reimplements the same `placeOrder`/`withdraw` logic without the reconciliation fix present upstream.

### Recommendation
In the Tron `IntentGatewayV2.placeOrder`, mirror the reconciliation used in `evm/src/apps/IntentGatewayV2.sol`: snapshot the contract's token balance before and after `safeTransferFrom` (and after the predispatch sweep), and compute `reducedInputs`/escrow credit from the *actual* received delta rather than the nominal `order.inputs[i].amount`. Additionally, consider making `withdraw()` tolerant of ledger/balance mismatches (e.g., cap the transferred amount to `min(recorded amount, actual balance)`) so that pre-existing bad escrow entries are not permanently unrecoverable.

### Proof of Concept
1. Deploy a fee-on-transfer ERC20 (e.g., 1% fee on transfer, as in `FeeOnTransferToken` used in `evm/tests/foundry/IntentGatewayV2SameChainTest.sol`).
2. User calls `placeOrder` on the Tron `IntentGatewayV2` with this token as `order.inputs[0]`, amount = 1000e18, via the non-predispatch path.
3. `safeTransferFrom` moves 1000e18 nominal but the gateway actually receives only 990e18 (1% fee taken); `_orders[commitment][token]` is nonetheless credited with `reducedInputs[0].amount` computed from the nominal 1000e18 (minus protocol fee), overstating the real balance held.
4. A solver fills the order (or the user cancels it), triggering `withdraw()` with `amount` equal to the overstated escrow value.
5. `token.call(transfer(beneficiary, amount))` reverts because the gateway's actual balance (990e18-ish) is less than `amount`; `withdraw()` reverts with `TransferFailed()`.
6. No other function path can release this escrow entry — the deposited tokens are permanently stuck.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L356-374)
```text
        TokenInfo[] memory reducedInputs;
        bytes32 commitment;

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
