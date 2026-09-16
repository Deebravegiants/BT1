## Title
Rebasing/interest-bearing (e.g. aToken-style) input tokens desynchronize the shared escrow pool in IntentGatewayV2, freezing funds for order participants on negative rebases - (`evm/src/apps/intentsv2/IntentsBase.sol`)

### Summary
`IntentGatewayV2` accepts arbitrary ERC-20 tokens as order inputs with no allowlist, and tracks each order's escrowed balance as a fixed integer amount in a shared per-token accounting map (`_orders[commitment][token]`), while the actual tokens for *all* concurrently open orders in that token sit together in the contract's single token balance. This is the same architectural flaw as the referenced Vault.sol report: fixed-amount bookkeeping against a balance that can independently change (rebase), rather than share-based accounting.

### Finding Description
When a user places an order, the escrowed amount is recorded as a static number: [1](#0-0) 

For redemption/refund, `_withdraw` decrements this stored value and transfers the *exact recorded amount* out via `safeTransfer`, with no re-check against actual live balance beyond the ERC20 call itself: [2](#0-1) 

Because many independent orders using the same input token share one contract-wide token balance, the system implicitly assumes `sum(_orders[*][token]) == token.balanceOf(gateway)`. If `token` is a rebasing/interest-accruing asset (e.g. an Aave aToken, stETH-style rebasing token), this invariant breaks:

- **Positive rebase**: `balanceOf(gateway)` grows over time without any order's stored value increasing. The excess is unaccounted for — it is not credited to the user who owns those escrowed funds, and the only way to remove it is `SweepDust`/`_sweepDust`, a Hyperbridge-governance-only path that sends the surplus to an arbitrary protocol beneficiary rather than the token's rightful owner (the escrowing user), effectively confiscating accrued yield that belongs to depositors.
- **Negative rebase** (or any external mechanic that reduces the token's reported balance for the holder over time, common for some interest-bearing wrapped tokens during redemption/settlement lag): the pooled `balanceOf(gateway)` can fall below `sum(_orders[*][token])`. Since withdrawals transfer the exact stored amount rather than a proportional share, whichever order is redeemed last will find the contract's real balance insufficient, and `safeTransfer` reverts — permanently freezing that user's/solver's escrowed funds, since there is no mechanism to reduce a stale `_orders` entry to match the actually-available balance.

No token allowlist exists in `placeOrder` to prevent rebasing tokens from being used; any ERC-20 address can be supplied as `order.inputs[i].token`, matching the fee-on-transfer handling paths already present in the code (which only handle *transfer-time* deltas, not post-deposit balance drift): [3](#0-2) 

The identical pattern (fixed-amount escrow mapping vs. shared pooled balance) also exists in the Tron variant: [4](#0-3) 

### Impact Explanation
This is a Medium-severity fund-freezing issue: because the gateway pools multiple users' escrows of the same token into one balance while tracking obligations as fixed numbers, a rebasing input token causes either (a) protocol-side capture of user-owned rebase interest via `SweepDust`, or (b) genuine insolvency of the shared pool leading to permanently stuck escrow for later-settling users/solvers when the underlying balance shrinks relative to recorded obligations. This affects any deployment where a rebasing/interest-bearing token is accepted as an order input, which is not prevented by any allowlist in the contract.

### Likelihood Explanation
Likelihood is moderate: it requires a rebasing token to be used as an order's input asset, which the contract does not prevent. Given IntentGatewayV2's stated goal (per `docs/content/developers/evm/intent-gateway/overview.mdx`) of enabling arbitrary EVM-token intent swaps, and that popular yield-bearing tokens (aTokens, stETH-like assets) are common, users/integrators are likely to attempt using them as inputs, especially since the fee-on-transfer handling gives a false impression that "unusual" ERC-20 semantics are already well-supported.

### Recommendation
Either (1) explicitly disallow known rebasing/interest-bearing tokens via an admin-configurable denylist/allowlist enforced in `placeOrder`, or (2) redesign escrow accounting to be share-based per token (mirroring ERC-4626-style share accounting, similar to `StreamingYieldVault` in the same codebase) so that `_orders` entries represent a claim on a proportional share of the pooled balance rather than an absolute amount, and reconcile any balance drift (positive or negative) fairly across all outstanding orders for that token instead of allowing first-withdrawer-wins insolvency.

### Proof of Concept
1. Deploy `IntentGatewayV2` with `protocolFeeBps = 0` and an interest-bearing token `aToken` (rebasing) as a supported input.
2. User A places an order escrowing `1000 aToken`; `_orders[commitmentA][aToken] = 1000`. Contract balance = 1000.
3. User B places an order escrowing `1000 aToken`; `_orders[commitmentB][aToken] = 1000`. Contract balance = 2000.
4. A negative rebase event (or interest-bearing token redemption mechanics that reduce `balanceOf`) reduces the gateway's actual `aToken` balance to `1500` while `_orders` still records `1000 + 1000 = 2000` total owed.
5. Order A is settled first via `onAccept`/`_withdraw`, transferring the full recorded `1000 aToken` to its solver — succeeds, leaving contract balance at `500`.
6. Order B's settlement attempts to transfer its recorded `1000 aToken`; `safeTransfer` reverts because the contract only holds `500 aToken` — Order B's escrow is permanently stuck (no code path exists to reconcile the shortfall), freezing User B's/the solver's funds.

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

**File:** evm/src/apps/IntentGatewayV2.sol (L363-373)
```text
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

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L451-470)
```text
    function _withdraw(WithdrawalRequest memory body, bool isRefund, bool finalize) internal {
        address beneficiary = address(uint160(uint256(body.beneficiary)));
        if (finalize) _filled[body.commitment] = beneficiary;

        uint256 len = body.tokens.length;
        for (uint256 i; i < len; i++) {
            address token = address(uint160(uint256(body.tokens[i].token)));
            uint256 amount = body.tokens[i].amount;
            if (amount == 0) continue;

            uint256 escrowed = _orders[body.commitment][token];
            if (escrowed == 0) revert UnknownOrder();

            _orders[body.commitment][token] = escrowed - amount;
            if (token == address(0)) {
                _sendValue(beneficiary, amount);
            } else {
                IERC20(token).safeTransfer(beneficiary, amount);
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
