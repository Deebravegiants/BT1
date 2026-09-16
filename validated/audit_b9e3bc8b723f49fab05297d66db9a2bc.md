Found it. In the Tron `IntentGatewayV2.cancelOrder()` (same-chain path, line 536-539), `WithdrawalRequest.tokens` is built directly from `order.inputs` (the original order amounts), not from the *remaining* escrowed amounts as in the audited EVM `IntentsBase._cancelSameChain` (which recomputes `remainingTokens[i]` from `_orders[commitment][token]`). This means if the order was even partially filled earlier via `fillOrder` (which decrements `_orders[commitment][token]` for the specific input tokens consumed, exactly analogous to `refundDeposit` silently reducing/removing a deposit without cleaning up any downstream accounting list), a subsequent `cancelOrder()` call passes the *original, full* input amounts into `withdraw()`.

`withdraw()` (lines 691-714) then iterates every token in `body.tokens` and unconditionally does:
```solidity
if (_orders[body.commitment][token] == 0) revert UnknownOrder();
...
_orders[body.commitment][token] -= amount;
``` [1](#0-0) 
There is no `if (amount == 0) continue;` guard (present in the audited EVM `IntentsBase._withdraw`, [2](#0-1) ), and no re-derivation of the *actual remaining* escrow per token (present in `_cancelSameChain`, [3](#0-2) ). So on Tron, once any input token of a multi-input order has been fully drained by a prior partial fill (escrow reduced to 0, exactly like the report's "refund transfers tokens but never updates the accounting used by later iteration"), the owner's legitimate `cancelOrder()` for the *remaining* tokens will underflow-subtract or hit `_orders[...]==0` and revert with `UnknownOrder()`, permanently freezing the user's still-escrowed input tokens on the other input entries — since the whole `withdraw()` loop reverts atomically.

### Title
Same-chain `cancelOrder` on Tron reverts and permanently freezes remaining escrow after a partial fill drains one input token - (File: evm/tron/contracts/apps/IntentGatewayV2.sol)

### Summary
On the Tron `IntentGatewayV2`, `cancelOrder()`'s same-chain path builds the refund `WithdrawalRequest` from the order's original `order.inputs` amounts instead of the currently escrowed balances, and the shared `withdraw()` function reverts the entire loop if any single token's escrow balance is zero. A prior partial fill that fully consumes one input token permanently blocks cancellation/refund of the order's other still-escrowed inputs.

### Finding Description
`placeOrder` escrows each input token independently in `_orders[commitment][token]` [4](#0-3) . `fillOrder`/partial-fill logic (mirrored from `IntrinsicIntents._fillSameChain`) decrements per-token escrow proportionally as fills happen, potentially draining one input token to zero while others remain escrowed — this is the direct analog of the audit report's `refundDeposit`, which removes funds from one deposit slot without updating any aggregate bookkeeping used by later code paths.

When the owner later calls `cancelOrder()` on the same chain, the withdrawal request is built using the *original* `order.inputs` array verbatim:
```solidity
WithdrawalRequest memory body =
    WithdrawalRequest({commitment: commitment, tokens: order.inputs, beneficiary: order.user});
withdraw(body, true);
``` [5](#0-4) 

`withdraw()` then iterates every token unconditionally:
```solidity
for (uint256 i; i < len;) {
    address token = ...;
    uint256 amount = body.tokens[i].amount;
    if (_orders[body.commitment][token] == 0) revert UnknownOrder();
    ...
    _orders[body.commitment][token] -= amount;
    unchecked { ++i; }
}
``` [1](#0-0) 

There is no check that `amount == 0` before the `_orders[...] == 0` revert check, and no re-derivation of the remaining escrowed amount per token — unlike the corresponding audited EVM implementation, which recomputes remaining balances (`_cancelSameChain`, [6](#0-5) ) and skips zero amounts in `_withdraw` ( [7](#0-6) ).

Consequently, if a multi-input order has one input token fully consumed by a prior partial fill (escrow == 0 for that token, but nonzero `amount` still present in `order.inputs[i]`), the `_orders[body.commitment][token] == 0` check reverts, and the entire cancellation transaction reverts atomically — blocking recovery of the *other* input tokens that are still legitimately escrowed.

### Impact Explanation
This permanently freezes the user's remaining escrowed input tokens for any multi-input order that has been partially filled asymmetrically across input tokens (only possible when different inputs are consumed unequally, which can happen given proportional-fill/rounding or `remaining == 0` bail-out logic per-output-token in the fill loop). The user cannot cancel or ever recover the residual escrow, since `cancelOrder`'s only refund code path always reverts. Funds become permanently stuck in the contract with no recovery mechanism — a direct freezing-of-funds impact, matching the severity class of the original report (one accounting-desynced entry bricking the entire settlement/refund flow).

### Likelihood Explanation
Reaching this state requires only: (1) a user placing a same-chain, multi-input order, (2) a solver partially filling it such that at least one input token's escrow is fully drained while another remains (achievable naturally through the existing partial-fill mechanics, no privileged action needed), and (3) the user calling the standard, unprivileged `cancelOrder()`. All actors involved (order owner, solver) are ordinary unprivileged users interacting with public entry points, so likelihood is high once such orders exist.

### Recommendation
In the Tron `cancelOrder()` same-chain branch, mirror `IntrinsicIntents._cancelSameChain`: recompute the `tokens` array for the `WithdrawalRequest` from the *current* `_orders[commitment][token]` balances (not `order.inputs`), and add a zero-amount skip (`if (amount == 0) continue;`) inside `withdraw()` before the `UnknownOrder` check, so tokens with no remaining escrow don't block the refund of tokens that do.

### Proof of Concept
1. User places a same-chain order with two input tokens, `A` and `B`, each escrowed via `placeOrder`.
2. A solver calls the same-chain fill path with a fill that fully consumes token `A`'s corresponding output requirement but only partially fills the leg driving token `B`'s release (achievable when different output assets reach `remaining == 0` at different times, or through fill ordering that fully drains one input's escrow while leaving the other nonzero) — after this, `_orders[commitment][A] == 0` while `_orders[commitment][B] > 0`.
3. User calls `cancelOrder(order, options)`. `withdraw()` iterates `order.inputs`, hits token `A` first (or in any order), sees `_orders[commitment][A] == 0`, and reverts with `UnknownOrder()`.
4. The transaction reverts entirely — token `B`'s legitimately remaining escrow can never be withdrawn, and since `cancelOrder` is the only refund path, the funds are permanently frozen.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L440-468)
```text
                // Store reduced amount (after protocol fees) in escrow
                _orders[commitment][token] += reducedInputs[i].amount;

                unchecked {
                    ++i;
                }
            }

            // Execute transfer calls from call dispatcher
            ICallDispatcher(dispatcher).dispatch(abi.encode(transferCalls));
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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L536-539)
```text
            WithdrawalRequest memory body =
                WithdrawalRequest({commitment: commitment, tokens: order.inputs, beneficiary: order.user});

            withdraw(body, true);
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L696-714)
```text
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

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L455-469)
```text
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
```

**File:** evm/src/apps/intentsv2/IntrinsicIntents.sol (L159-180)
```text
    function _cancelSameChain(Order calldata order, bytes32 commitment) internal {
        if (order.user != bytes32(uint256(uint160(msg.sender)))) revert Unauthorized();

        uint256 inputsLen = order.inputs.length;
        TokenInfo[] memory remainingTokens = new TokenInfo[](inputsLen);
        bool hasEscrow = false;
        for (uint256 i; i < inputsLen;) {
            address token = address(uint160(uint256(order.inputs[i].token)));
            uint256 escrowed = _orders[commitment][token];
            if (escrowed > 0) hasEscrow = true;
            remainingTokens[i] = TokenInfo({token: order.inputs[i].token, amount: escrowed});
            unchecked {
                ++i;
            }
        }
        if (!hasEscrow) revert UnknownOrder();

        WithdrawalRequest memory body =
            WithdrawalRequest({commitment: commitment, tokens: remainingTokens, beneficiary: order.user});

        _withdraw(body, true, true);
    }
```
