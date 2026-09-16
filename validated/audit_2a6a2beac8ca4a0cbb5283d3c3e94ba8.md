## Analysis

The reported bug class — fee-on-transfer tokens that revert on zero-value transfers blocking a settlement/liquidation action — has a concrete analog in Hyperbridge's Tron intent-gateway contract.

The canonical EVM `IntentsBase._withdraw` function explicitly guards against this by skipping zero-amount token legs before attempting a transfer: [1](#0-0) 

However, the Tron variant's equivalent `withdraw()` function does **not** carry this guard. It only checks that the token's *total remaining escrow* is non-zero, not that the specific `amount` being transferred in this call is non-zero, and then unconditionally calls `token.call(transfer(beneficiary, amount))`: [2](#0-1) 

### Title
Tron `IntentGatewayV2.withdraw` lacks a zero-amount transfer guard, allowing fee-on-transfer tokens that revert on zero transfers to permanently block escrow release - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The Tron deployment of `IntentGatewayV2` implements escrow release/refund in a `withdraw()` function that iterates over `WithdrawalRequest.tokens` and calls `token.transfer(beneficiary, amount)` for every entry without first checking `amount == 0`. The parallel, more recently hardened EVM implementation (`IntentsBase._withdraw`) does have `if (amount == 0) continue;`, indicating this exact class of bug was already recognized and patched on the main EVM contract but not on the Tron variant.

### Finding Description
`withdraw()` checks only that the token's aggregate escrow balance (`_orders[body.commitment][token]`) is non-zero before transferring — not that the per-call `amount` for that token is non-zero: [3](#0-2) 

If any token used as an order input becomes (or is upgraded to) a fee-on-transfer token that reverts when the transferred amount is zero — a scenario the protocol already explicitly anticipates and tests for on the main EVM path (see `FeeOnTransferToken` test fixture) — a `WithdrawalRequest` containing a zero-amount leg for that token (e.g., resulting from partial-fill proportional-amount rounding down to zero, `inputs[i].amount × fillAmount / totalRequired`) will cause the entire `withdraw()` call, and therefore the whole `onAccept`/`onGetResponse`/fill transaction, to revert.

Because `withdraw()` is atomic across all tokens in the request, a single zero-amount leg blocks release of every other (non-zero) token in the same call as well.

### Impact Explanation
This blocks legitimate escrow release/refund flows (the functional analog of "liquidation" for this codebase) for affected orders, causing the escrowed funds to become permanently stuck if the zero-amount condition is deterministic for that order (e.g., a fixed rounding-to-zero fraction on a multi-asset partial fill). This matches the "permanent freezing of funds" acceptance criterion.

### Likelihood Explanation
Likelihood depends on (a) an order using a fee-on-transfer token that reverts on zero transfers, and (b) a code path producing a zero `amount` entry for that token within `WithdrawalRequest.tokens` (most plausibly via same-chain partial-fill proportional math, which can round to zero for very small fill fractions on a given token). The main EVM contract's already-implemented guard `if (amount == 0) continue;` and the fee-on-transfer regression tests confirm the maintainers treat this scenario as reachable and worth defending against — the Tron contract's `withdraw()` was not updated to match.

### Recommendation
Add the same `if (amount == 0) continue;` guard used in `IntentsBase._withdraw` to the Tron `withdraw()` function before attempting each token transfer, so zero-amount legs are skipped instead of attempted.

### Proof of Concept
1. Register an ERC20 input token that reverts on `transfer(to, 0)` (fee-on-transfer token style) as an order input on the Tron gateway.
2. Construct a same-chain order with multiple input/output token pairs such that a partial fill computes `inputs[i].amount × fillAmount / totalRequired == 0` for that token.
3. Call `fillOrder` (or trigger `onAccept`/`onGetResponse` for cross-chain refund/redeem) so `withdraw()` is invoked with a `WithdrawalRequest.tokens` array containing a `0`-amount entry for that token while `_orders[commitment][token] > 0`.
4. `withdraw()` reaches `token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, 0))`, which reverts because the token disallows zero-value transfers.
5. The entire `withdraw()` call reverts, so no tokens in the request are released, and the affected order's escrow remains permanently locked as long as the rounding condition persists.

### Citations

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L455-470)
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
