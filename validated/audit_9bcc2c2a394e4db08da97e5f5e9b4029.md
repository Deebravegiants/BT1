## Title
Order placer can escrow an arbitrary/malicious ERC-20 as an intent input, permanently freezing escrow and blocking solver repayment - (File: `evm/src/apps/intentsv2/IntentsBase.sol`)

### Summary
`IntentGatewayV2.placeOrder` (and its variants in `IntrinsicIntents.sol` / `ExtrinsicIntents.sol` / the tron port) accepts any ERC-20 address encoded as `order.inputs[i].token` with no token whitelist or safety check, and escrows it via `safeTransferFrom`. The single escrow-release routine `_withdraw` in `evm/src/apps/intentsv2/IntentsBase.sol` later loops over *every* token recorded for that commitment and does an unconditional `IERC20(token).safeTransfer(beneficiary, amount)` for each one in a single transaction. Any order placer can therefore include a malicious/adversarial ERC-20 (pausable, blacklist-gated, or one that simply reverts on transfer to certain addresses) among the order's `inputs`. Because `_withdraw` reverts entirely if any single token transfer reverts, the whole withdrawal — fill settlement, cancellation, or refund — becomes permanently unexecutable, freezing every token escrowed under that commitment, not just the malicious one.

### Finding Description
`placeOrder` transfers input tokens into escrow with no allow-listing of `order.inputs[i].token`: [1](#0-0) 

The escrowed balances are tracked per `(commitment, token)` in `_orders`, and all release paths — successful cross-chain fill (`RedeemEscrow`), cross-chain refund (`RefundEscrow`), and same-chain cancel — funnel through the shared `_withdraw` function: [2](#0-1) 

This loop has no per-token try/catch or skip-on-failure logic: if `IERC20(token).safeTransfer(beneficiary, amount)` reverts for *any* one of the tokens bundled under the commitment, the entire `_withdraw` call reverts, and with it the entire enclosing transaction (`onAccept` for cross-chain, or the same-chain `fillOrder`/`cancelOrder` call). An order placer fully controls which tokens go into `order.inputs`, so they can mint/deploy an ERC-20 whose `transfer`/`transferFrom` unconditionally reverts (or reverts once a toggle/blacklist is flipped after escrow), exactly the "evil token" pattern described in the reference report. Because there is no whitelist check anywhere in the intents escrow path (unlike, e.g., `WrappedHyperFungibleToken`, which only ever moves its own configured `_underlying`), this is directly reachable by any unprivileged user who calls `placeOrder`.

### Impact Explanation
- **Cross-chain fill griefing / solver fund loss**: in `_fillCrossChain`, the solver first delivers output tokens to the beneficiary and *then* dispatches the `RedeemEscrow` message: [3](#0-2)  When the relayed message reaches the source chain and `onAccept` calls `_withdraw` to pay the solver from escrow, a poisoned token in the same order permanently reverts that payout. The solver has already paid the output side and can never be repaid — a direct, permanent loss of solver funds.
- **Permanent freezing of user escrow**: same-chain fill, cancel-from-source, and cancel-from-destination all terminate in `_withdraw` as well. Once a bad token is escrowed, the order can never be filled, cancelled, or refunded — the escrowed value (including any *other*, legitimate token bundled in the same order and any Hyperbridge relayer fees held under `TRANSACTION_FEES`) is permanently locked, satisfying "permanent freezing of funds."
- Reachable from a single `placeOrder` transaction by any unprivileged user — no governance/admin/relayer compromise required.

### Likelihood Explanation
High. `placeOrder` is fully permissionless and performs no token validation; a griefer only needs to deploy a trivial ERC-20 with a `transfer`/`transferFrom` that can be made to always revert (or made to revert after the order is placed and a solver has already committed output funds), then place an order using it as one of the `inputs`. This requires no special privileges, timing races, or governance interaction.

### Recommendation
- Restrict `order.inputs[i].token` (and predispatch asset tokens) to a governance-maintained token whitelist before accepting escrow in `placeOrder`, mirroring how other token bridge components restrict to a single, vetted `_underlying` token.
- Make `_withdraw` resilient to a single misbehaving token: use a low-level `call`/try-catch per token transfer, and if a transfer fails, retain the escrow for that specific token (e.g., mark it recoverable/claimable separately) instead of reverting the whole withdrawal, so unaffected tokens and the finalize/fee-release logic still complete.
- Alternatively, add a governance-only "force-skip" or "sweep" path for tokens that have become non-transferable, so escrow tied to malicious tokens can eventually be evicted rather than locked forever.

### Proof of Concept
1. Attacker deploys `EvilToken` (ERC-20) whose `transfer`/`transferFrom` succeeds during `placeOrder`'s pull-in but can later be toggled (via a `pause()`-like admin-controlled function on the token itself, held by the attacker) to always `revert()`.
2. Attacker calls `IntentGatewayV2.placeOrder` with `order.inputs = [ {token: EvilToken, amount: X} ]` (optionally alongside a legitimate token in the same `inputs` array to maximize damage) and a valid, fillable `output`.
3. A solver fills the order: for a cross-chain order, the solver sends the output assets to the beneficiary and the gateway dispatches a `RedeemEscrow` message (`_fillCrossChain`, `evm/src/apps/intentsv2/ExtrinsicIntents.sol:207-212`).
4. Before/at message delivery, attacker calls `EvilToken.pause()` (toggle transfers to always revert).
5. When the relayed message reaches the source chain, `onAccept` invokes `_withdraw`, which attempts `IERC20(EvilToken).safeTransfer(solver, amount)` and reverts (`evm/src/apps/intentsv2/IntentsBase.sol:451-470`), causing the entire delivery/withdraw transaction to revert. The solver, who already delivered the output tokens in step 3, never receives the escrowed input tokens, and — since any co-escrowed legitimate token in the same commitment is looped over in the same reverting call — those funds are frozen as well, with no retry path that bypasses the bad token.

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

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L191-212)
```text
            } else {
                IERC20(token).safeTransferFrom(msg.sender, beneficiary, totalRequired + beneficiaryShare);
                if (protocolShare > 0) {
                    IERC20(token).safeTransferFrom(msg.sender, address(this), protocolShare);
                }
            }
            if (protocolShare > 0) emit DustCollected(token, protocolShare);
            outputFills[i] = TokenInfo({token: outputToken, amount: totalRequired});
        }

        _execute(order, outputsLen);

        // Native dispatch fee only if the solver sent enough to cover it; else the fee token.
        uint256 nativeFee = options.nativeDispatchFee;
        if (nativeFee > msgValue) nativeFee = 0;
        msgValue -= nativeFee;
        _post(
            order,
            _body(RequestKind.RedeemEscrow, commitment, order.inputs, bytes32(uint256(uint160(msg.sender)))),
            options.relayerFee,
            nativeFee
        );
```
