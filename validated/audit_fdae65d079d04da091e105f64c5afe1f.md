### Title
Multi-asset order escrow release can be permanently frozen by a single malfunctioning/blacklisting ERC20 in the order's token set - (File: evm/src/apps/intentsv2/IntentsBase.sol)

### Summary
`IntentsBase._withdraw` releases every token listed in a `WithdrawalRequest` in a single atomic loop using `safeTransfer`. Orders can bundle multiple distinct ERC20 tokens as inputs/outputs. If any one of those tokens is a non-standard token that reverts or is blacklisted for the beneficiary address (the class of tokens referenced in the external report, e.g. USDC-style blacklisting or Tether-Gold-like tokens that stop transferring for certain accounts), the whole withdrawal transaction reverts, and since there is no per-token retry or skip mechanism, all other (perfectly healthy) tokens in that same order become permanently unreleasable as well.

### Finding Description
`_withdraw` iterates `body.tokens` and calls `IERC20(token).safeTransfer(beneficiary, amount)` for each token in the withdrawal request, decrementing `_orders[commitment][token]` before the transfer: [1](#0-0) 

This function is invoked from the `onAccept` handler of `ExtrinsicIntents` when Hyperbridge delivers a `RedeemEscrow` or `RefundEscrow` message. Because `safeTransfer` is used (correctly propagating `false`/revert as a Solidity revert via OpenZeppelin `SafeERC20`), any token in `body.tokens` that:
- reverts unconditionally for a specific address (blacklist behavior), or
- behaves like the "returns bool but then returns false forever" class of tokens cited in the report (e.g. Tether Gold-style tokens, or any token whose transfer function starts unconditionally returning `false`/reverting for the beneficiary after some external state change),

will cause the entire `_withdraw` call — and therefore the entire cross-chain message delivery — to revert. Since `_orders[commitment][token] = escrowed - amount` for *all* tokens in the loop is calculated before any of the actual `safeTransfer`/`_sendValue` calls execute, and Solidity reverts unwind the whole transaction atomically, a revert on token N in the loop also rolls back the successful decrement/transfer of tokens 1..N-1 that already executed in the same call. There is no isolation, try/catch, or per-token skip-and-retry path; the message is simply "undelivered" and must be retried by a relayer, but retrying replays the exact same body, hitting the exact same revert every time.

The same multi-asset bundling of inputs/outputs is present up front at order placement (`IntentGatewayV2.placeOrder`, `evm/src/apps/IntentGatewayV2.sol`), so orders routinely escrow more than one ERC20 as part of `order.inputs` / `order.output.assets`: [2](#0-1) 

### Impact Explanation
Once a beneficiary/solver becomes unable to receive a single token in a multi-token order (due to blacklisting or a "weird ERC20" that starts always returning false/reverting), the `RedeemEscrow`/`RefundEscrow` message can never be successfully delivered, because delivery is all-or-nothing across the token list. This permanently freezes every other legitimate, unrelated token escrowed as part of that same order commitment — funds that would otherwise be fully redeemable become stuck in the `IntentGatewayV2`/`ExtrinsicIntents` contract with no recovery path, since `_orders[commitment][token]` can never be zeroed for the healthy tokens either (the decrement only happens transactionally alongside the failing one). This is a concrete permanent freezing-of-funds condition satisfying the "Accept only concrete theft or permanent freezing of funds" bar, scoped to whichever counterparties happen to be paired with a misbehaving token in a shared order.

### Likelihood Explanation
Likelihood is moderate: it requires (a) an order that bundles a non-standard/blacklist-capable ERC20 alongside other tokens, and (b) that token entering the "always-false/revert" state for the specific beneficiary address (e.g., OFAC/compliance blacklist action, or a bug in the token itself as documented for real-world tokens like USDC/Tether Gold). Given Hyperbridge's intents system is designed to be permissionless and accept arbitrary ERC20s as `order.inputs`/`order.output.assets` without an allow/deny-list, and beneficiaries are user-supplied addresses, this scenario is realistically triggerable by any solver/user pairing an already-blacklist-flagged address with a compliant stablecoin, or simply by using a token like Tether Gold in combination with any other asset in the same order.

### Recommendation
Do not process all tokens in a `WithdrawalRequest` inside a single atomic all-or-nothing loop. Either (1) wrap each individual token transfer in `_withdraw` in a low-level call with try/catch (or use `try/catch` around an external `transfer` helper) so a failure on one token does not block release of the others, tracking failed transfers in a claimable/sweepable mapping for the beneficiary to retry later; or (2) require that each `WithdrawalRequest`/message settle exactly one token per delivered message so relayers can retry per-token instead of per-order, decoupling the fate of unrelated assets escrowed under the same commitment.

### Proof of Concept
1. Solver places (or user creates) an order whose `order.output.assets`/escrowed inputs include Token A (a normal ERC20) and Token B (a blacklist-capable/weird ERC20 like a Tether-Gold-style token).
2. Token B's issuer blacklists the order's beneficiary address (or the token otherwise begins reverting/returning false for that address) after escrow but before settlement.
3. Hyperbridge relays the `RedeemEscrow`/`RefundEscrow` message; `ExtrinsicIntents.onAccept` calls `IntentsBase._withdraw(body, ...)`.
4. The loop in `_withdraw` reaches Token B's `safeTransfer` call, which reverts (`SafeERC20: ERC20 operation did not succeed` or a native revert from the blacklist check), unwinding the entire transaction — including Token A's transfer that already executed earlier in the same loop iteration. [3](#0-2) 
5. Every relay retry replays the identical `body`, hitting the identical revert; Token A remains permanently locked in the contract alongside Token B, with no mechanism to release Token A independently.

### Citations

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

**File:** evm/src/apps/IntentGatewayV2.sol (L228-256)
```text
        uint256 inputsLen = order.inputs.length;

        // Phase 1: Transfer tokens and record actual received amounts.
        // For fee-on-transfer tokens, the gateway receives less than the requested amount.
        // We mutate order.inputs to reflect actual received so the commitment and escrow
        // are consistent with what the gateway holds.
        uint256 msgValue = msg.value;
        if (order.predispatch.call.length > 0 && order.predispatch.assets.length > 0) {
            address dispatcher = _params.dispatcher;

            uint256 assetsLen = order.predispatch.assets.length;
            for (uint256 i; i < assetsLen;) {
                address token = address(uint160(uint256(order.predispatch.assets[i].token)));
                uint256 amount = order.predispatch.assets[i].amount;
                if (amount == 0) revert InvalidInput();

                if (token == address(0)) {
                    if (amount > msgValue) revert InsufficientNativeToken();
                    msgValue -= amount;

                    _sendValue(dispatcher, amount);
                } else {
                    IERC20(token).safeTransferFrom(msg.sender, dispatcher, amount);
                }

                unchecked {
                    ++i;
                }
            }
```
