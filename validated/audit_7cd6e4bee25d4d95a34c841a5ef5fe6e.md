### Title
Fee-on-transfer tokens cause escrow over-crediting in Tron `IntentGatewayV2.placeOrder` due to missing balance-delta check - (File: evm/tron/contracts/apps/IntentGatewayV2.sol)

### Summary
`IntentGatewayV2.placeOrder` on the Tron deployment computes the order commitment and the escrowed amount recorded in `_orders[commitment][token]` from the user-supplied `order.inputs[i].amount` *before* any token transfer occurs, and then simply calls `IERC20(token).safeTransferFrom(msg.sender, address(this), order.inputs[i].amount)` without verifying how much the gateway actually received.

### Finding Description
In the non-predispatch branch of `placeOrder`: [1](#0-0) 
the code performs `safeTransferFrom` for `order.inputs[i].amount` and then unconditionally credits `_orders[commitment][token] += reducedInputs[i].amount` — where `reducedInputs` was derived earlier from the original, unadjusted `order.inputs[i].amount` at lines 356-385 (computed before the transfer even happens).

This is the exact bug class from the external report: `safeTransferFrom`'s return value is technically checked by `SafeERC20` (it reverts on `false`/non-compliant returns), but the contract never checks the **balance delta** to detect fee-on-transfer tokens. For any ERC20 that deducts a fee on transfer, the gateway will receive less than `order.inputs[i].amount`, yet it records the full (fee-inclusive) `reducedInputs[i].amount` as escrowed for that token in `_orders`.

This is a direct regression relative to the sibling EVM implementation, `evm/src/apps/IntentGatewayV2.sol`, which explicitly guards against this by snapshotting balances before/after transfer and mutating `order.inputs[i].amount` to the actual amount received: [2](#0-1) 
The Tron contract at lines 450-468 lacks this balance-based correction entirely, and the commitment/escrow bookkeeping (lines 356-385) is fixed before the transfer, so it cannot reflect any shortfall even if a delta check were added later.

### Impact Explanation
Because `_orders[commitment][token]` is over-credited relative to the gateway's true on-chain balance for that token, the contract's internal accounting becomes inconsistent with reality. Withdrawal/redemption paths (`withdraw`, `cancelOrder`'s same-chain refund, and `RedeemEscrow` handling) rely on `_orders[commitment][token]` to determine payout amounts. Over time, as multiple orders using fee-on-transfer tokens are placed, the aggregate recorded escrow across all commitments will exceed the gateway's actual token balance. This leads to a shared-pool insolvency: legitimate escrow withdrawals for other orders can fail (denial of funds/freezing) or, depending on withdrawal ordering, allow one order's inflated escrow entry to be paid out using funds that were actually deposited by a different order — effectively draining other users' escrowed collateral. This satisfies the "unbacked mint"/accounting-desync criteria for a Medium-severity finding involving permanent freezing or unauthorized draw against pooled funds.

### Likelihood Explanation
Likelihood is credible but conditional: it is triggered only when a fee-on-transfer (or similarly non-standard) ERC20 token is configured as an order input asset. Given IntentGatewayV2 is a general-purpose, permissionless intents/token-bridging entry point intended to support arbitrary ERC20 inputs (as evidenced by the EVM sibling contract explicitly handling this exact case with tests, e.g. `evm/tests/foundry/IntentGatewayV2SameChainTest.sol`), fee-on-transfer token support is a realistic and reachable scenario for the Tron deployment, reachable by any unprivileged user calling `placeOrder` with such a token and no special privileges required.

### Recommendation
Mirror the EVM implementation's balance-delta pattern in the Tron `IntentGatewayV2.placeOrder`: measure `IERC20(token).balanceOf(address(this))` before and after each `safeTransferFrom`, use the actual received delta (not the requested `order.inputs[i].amount`) both when computing `reducedInputs`/the commitment and when crediting `_orders[commitment][token]`, and reject or account for the difference (e.g. treat shortfall as dust or revert if it invalidates minimum requirements) — consistent with the protections already present in `evm/src/apps/IntentGatewayV2.sol`.

### Proof of Concept
1. Configure an ERC20 token with a transfer fee (e.g. deducts 5% on `transferFrom`) as an order input on the Tron `IntentGatewayV2`.
2. Call `placeOrder` with `order.inputs[0].amount = 100` of that token; user approves 100 for the gateway.
3. `safeTransferFrom(msg.sender, address(this), 100)` executes; gateway actually receives 95 tokens (5 tokens taken as fee), but `_orders[commitment][token]` is credited with `reducedInputs[0].amount` derived from the full 100 (minus protocol fee, if any) — an amount the gateway never actually held.
4. Repeat with additional orders using the same fee-on-transfer token; the sum of all `_orders[...][token]` entries now exceeds `IERC20(token).balanceOf(address(this))`.
5. When orders are later withdrawn/refunded via `withdraw`/`cancelOrder`, the last such withdrawal(s) against this token will fail due to insufficient balance, freezing funds for whichever legitimate order is unable to be paid — or, depending on internal accounting nuances of `withdraw`, an attacker's inflated escrow record could be redeemed ahead of others, effectively at the expense of other users' deposits.

*Note: The exact `withdraw` function body (lines beyond what was retrieved) was not fully inspected in this session due to iteration limits, so the precise downstream mechanics of over-credited escrow redemption (revert vs. cross-order fund drain) were not fully confirmed by reading `withdraw`'s implementation; a full review of `withdraw` and `RedeemEscrow` handling in `evm/tron/contracts/apps/IntentGatewayV2.sol` is recommended to confirm the exact failure mode.*

### Citations

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

**File:** evm/src/apps/IntentGatewayV2.sol (L312-328)
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
```
