### Title
Permanent freezing of escrowed intent funds when settlement transfers revert on blacklisted beneficiaries - ([File: evm/src/apps/intentsv2/IntentsBase.sol])

### Summary
`IntentsBase._withdraw`, which is invoked from `onAccept` for `RedeemEscrow`/`RefundEscrow` messages and from `onGetResponse` for source-chain cancellations, transfers escrowed ERC-20 tokens directly to a `beneficiary` address via `safeTransfer` with no fallback or two-step claim mechanism. If that token enforces an address blacklist (e.g. USDC) and the beneficiary (solver or user) is blacklisted, the transfer reverts, the entire settlement transaction reverts, and — because no `onPostRequestTimeout`/timeout recovery path exists for `RedeemEscrow`/`RefundEscrow` dispatches (`timeout: 0` is used for the cancel `DispatchGet`, and no timeout handler exists in `IntentsBase`/`ExtrinsicIntents`/`IntrinsicIntents`) — the escrowed funds tied to that specific order commitment become permanently unrecoverable.

### Finding Description
Cross-chain order settlement in the Hyperbridge Intents system funnels through `IntentsBase._withdraw`: [1](#0-0) 

This function is called:
- From `ExtrinsicIntents.onAccept` for `RequestKind.RedeemEscrow` (solver claims escrowed input tokens after filling on destination) and `RequestKind.RefundEscrow` (user reclaims escrow after cancelling from destination): [2](#0-1) 
- From `onGetResponse`, refunding escrow after a source-chain cancellation is proven unfilled.

`_withdraw` first marks the order finalized (`_filled[body.commitment] = beneficiary`) then performs a direct `safeTransfer` to the beneficiary inside the same call: [3](#0-2) 

If the token being transferred blacklists the beneficiary address, `safeTransfer` reverts, which causes the entire `onAccept` (or `onGetResponse`) call to revert — including the `_filled` write. Because the ISMP host's delivery of this specific message will therefore never succeed (the same beneficiary/token pairing is retried by any relayer with the same result), and there is no `onPostRequestTimeout` handler defined anywhere in the intents contracts (`IntentsBase.sol`, `ExtrinsicIntents.sol`, `IntrinsicIntents.sol`) to allow the message to time out and re-route funds elsewhere, the escrowed tokens for that commitment become permanently stuck:
- A filling solver can never claim the input tokens it is owed (RedeemEscrow) if it is blacklisted for that input token.
- A cancelling user can never reclaim their escrow (RefundEscrow / GET-response refund) if they are blacklisted for the escrowed token.

There is no alternate withdrawal path, admin sweep, or two-step "pull" pattern for these specific per-order escrow balances — `SweepDust` only handles unrelated protocol dust, not order-specific escrow.

This is directly analogous to the reported GMX bug class: a hard-coded push-transfer to a caller-controlled beneficiary address inside a privileged settlement/process function, with no fallback if the ERC-20 transfer reverts, leading to permanently locked state for the affected flow.

### Impact Explanation
Impact is scoped per-order-commitment rather than globally (unlike the GMX report where the entire vault entered a stuck status blocking all users): this codebase's escrow accounting is per-commitment (`_orders[commitment][token]`), so a blacklisted beneficiary on one order does not block settlement of unrelated orders. However, for the specific affected order, the impact is a **permanent freeze of escrowed funds**:
- For a cross-chain fill, the input tokens escrowed by the user are permanently locked (the solver already delivered output tokens on the destination chain, so the user's side is irreversibly sunk, and the solver can never recoup the input tokens).
- For a cancellation refund, the user's own escrowed tokens become permanently unrecoverable.

This meets the "permanent freezing of funds" bar for a Medium/High severity finding on Hyperbridge's intents settlement path, since a single submitted order (a single unprivileged user/solver action) is sufficient to trigger it, and there is no recovery mechanism (no timeout, no admin rescue, no redirect-to-another-beneficiary option).

### Likelihood Explanation
Requires the beneficiary address (user or solver) to be blacklisted by the escrowed ERC-20's issuer (e.g., USDC/USDT-style tokens), which is realistic given the docs and tests in this codebase explicitly use USDC as an intents input/output token. This can occur accidentally (a solver's address gets blacklisted after being flagged) or be used adversarially by a user placing an order with an already-known-to-be-soon-blacklisted address, or a malicious order-creator intentionally targeting a solver they know is about to be sanctioned, in order to grief that solver's fill. Likelihood is moderate — it depends on external blacklist events, not on protocol logic flaws alone, but the protocol provides no mitigation once triggered.

### Recommendation
Adopt the two-step "hold and claim" pattern recommended in the original report: instead of pushing tokens directly to `beneficiary` inside `_withdraw`, credit an internal balance mapping (`claimable[beneficiary][token] += amount`) and let the beneficiary pull funds via a separate `claim()` function that specifies (or is later updatable to) a different receiving address. Additionally, consider adding timeout handling (`onPostRequestTimeout`) for `RedeemEscrow`/`RefundEscrow` dispatches so that failed settlements do not remain unresolved indefinitely, and/or allow beneficiaries (or governance) to redirect a stuck claim to an alternate address after some grace period.

### Proof of Concept
1. User places a same-chain-source, cross-chain-destination `Order` with `inputs = [USDC amount]`, escrowing USDC in `IntentGatewayV2`/`ExtrinsicIntents` on the source chain.
2. A solver fills the order on the destination chain via `fillOrder`, which dispatches a `RedeemEscrow` message back to the source chain naming the solver as beneficiary: [4](#0-3) 
3. Before the message is relayed and delivered, USDC's issuer blacklists the solver's address (e.g., due to unrelated compliance action).
4. A relayer submits the proof; the source-chain host calls `onAccept`, which calls `_withdraw`, which calls `IERC20(USDC).safeTransfer(solver, amount)` — this reverts because the solver is blacklisted: [5](#0-4) 
5. Every subsequent relayer retry of the same message hits the identical revert. No timeout handler exists to reroute or refund the escrow. The escrowed USDC for this commitment is permanently locked in the gateway contract, unclaimable by anyone.

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

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L207-212)
```text
        _post(
            order,
            _body(RequestKind.RedeemEscrow, commitment, order.inputs, bytes32(uint256(uint160(msg.sender)))),
            options.relayerFee,
            nativeFee
        );
```

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L330-337)
```text
    function onAccept(IncomingPostRequest calldata incoming) external override onlyHost {
        _checkRelayer(incoming.relayer);
        RequestKind kind = RequestKind(uint8(incoming.request.body[0]));
        if (kind == RequestKind.RedeemEscrow || kind == RequestKind.RefundEscrow) {
            _authenticate(incoming.request);
            WithdrawalRequest memory body = abi.decode(incoming.request.body[1:], (WithdrawalRequest));
            return _withdraw(body, kind == RequestKind.RefundEscrow, true);
        }
```
