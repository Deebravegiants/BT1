## Title
Fee-on-transfer ERC20 inputs are escrowed at face value instead of actual received amount in Tron `IntentGatewayV2.placeOrder`, causing under-collateralized escrow and cross-order fund drain - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The Tron variant of `IntentGatewayV2.placeOrder` pulls input tokens via `safeTransferFrom` and then unconditionally credits the `_orders` escrow mapping with the requested (fee-adjusted) amount, without verifying how many tokens the contract actually received. For fee-on-transfer ERC20 tokens, this causes the gateway's internal accounting to record more escrowed tokens than it actually holds — the exact bug class described in the referenced BvB report, where `withdrawableFees`/escrow bookkeeping assumed full transfer amounts land in the contract.

### Finding Description
In the non-predispatch branch of `placeOrder`: [1](#0-0) 

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

`reducedInputs[i].amount` is derived purely from `order.inputs[i].amount` (the user-specified amount minus the protocol fee bps) — it is never reconciled against the token's actual `balanceOf(address(this))` before/after the transfer. For a fee-on-transfer token, `safeTransferFrom` delivers less than `order.inputs[i].amount` to the gateway, yet the full `reducedInputs[i].amount` is still credited to `_orders[commitment][token]`.

The predispatch branch has the same defect: the dispatcher→gateway sweep transfers `balance` (the dispatcher's raw pre-fee balance) via `IERC20.transfer`, which itself may incur another transfer fee, yet the escrow is still credited with `reducedInputs[i].amount` computed from the *pre-transfer* required amount rather than what the gateway actually received: [2](#0-1) 

This is a regression relative to the main EVM `IntentGatewayV2.sol`, which was hardened against exactly this class of bug by measuring the actual balance delta after every transfer and mutating `order.inputs[i].amount` accordingly before computing the commitment/escrow: [3](#0-2) 

The Tron deployment never received this fix.

### Impact Explanation
Any unprivileged user can call `placeOrder` with a fee-on-transfer ERC20 as an input token. The gateway's `_orders[commitment][token]` mapping will record more tokens than the contract's real balance for that token. When the order is later filled and the escrow released (`_fillSameChain`/`_fillCrossChain`/redeem-escrow paths), the solver is paid out based on the inflated `_orders` value. Because escrow is a shared per-token balance across all outstanding orders, satisfying this inflated payout drains real tokens that belong to other users' unrelated escrowed orders in the same token — i.e., theft/insolvency of other users' funds — or, if the contract's balance is insufficient, the fill/redemption reverts, permanently freezing the shortfall and any order depending on it. This is a direct fund-safety issue reachable from a single `placeOrder` transaction.

### Likelihood Explanation
Likelihood is moderate-to-high in any deployment that allows arbitrary/permissionless input tokens (the general intent-gateway design does not appear to restrict input tokens to a fixed allowlist of "safe" ERC20s). Fee-on-transfer tokens are common on Tron/EVM-compatible chains, and no code path guards against them in this contract, whereas the sibling EVM contract explicitly was patched to handle this case — confirming it is a known, exploitable risk class for this codebase, just not addressed here.

### Recommendation
Mirror the EVM `IntentGatewayV2.sol` fix in the Tron variant: measure `IERC20(token).balanceOf(address(this))` before and after each `safeTransferFrom` (and after the predispatch dispatcher sweep) to determine the actual amount received, mutate `order.inputs[i]` to that real value, and derive `reducedInputs`/`commitment`/`_orders[commitment][token]` from the actual received amount rather than the caller-specified amount.

### Proof of Concept
1. Deploy a fee-on-transfer ERC20 (e.g., 1% fee) and mint balance to `user`.
2. `user` calls `placeOrder` with this token as an input, specifying `amount = 1000e18`.
3. `safeTransferFrom` delivers only `990e18` to the gateway (contract's real token balance increases by 990e18).
4. `_orders[commitment][token]` is nonetheless credited with `reducedInputs[i].amount` computed from `1000e18` (minus protocol fee, if any) — an amount greater than the 990e18 actually held.
5. When a solver fills the order and the escrow is released, the contract attempts to pay out the inflated escrowed amount for this token, which either reverts (freezing funds) or is satisfied using tokens escrowed for other users' orders in the same token (fund theft/insolvency).

This is directly analogous to the referenced BvB report's `withdrawableFees` miscalculation for fee-on-transfer tokens, but manifests here in the intents escrow accounting of `evm/tron/contracts/apps/IntentGatewayV2.sol`.

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
