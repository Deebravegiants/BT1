### Title
Multi-token order escrow release reverts entirely if any single input token has a pausable/blockable transfer, permanently freezing all co-escrowed assets - (File: evm/src/apps/intentsv2/IntentsBase.sol)

### Summary
`Order.inputs` is a `TokenInfo[]`, allowing a single order to escrow multiple distinct ERC-20 tokens in one commitment. Settlement (`_withdraw`) transfers every escrowed token to the beneficiary in one loop with no per-token isolation, mirroring the `VE3DRewardPool`/veToken bug class: any one token whose transfer can be blocked (pausable, blacklistable, e.g. USDC-style compliance freeze) reverts the entire loop, freezing every other token bundled in the same order.

### Finding Description
`Order` bundles arbitrary ERC-20 tokens together as escrow inputs: [1](#0-0) 

Settlement happens through `_withdraw`, which loops over `body.tokens` (== `order.inputs`) and unconditionally calls `IERC20(token).safeTransfer(beneficiary, amount)` for each, with no try/catch or per-token isolation: [2](#0-1) 

This function is invoked from `onAccept` on `RedeemEscrow`/`RefundEscrow` — the cross-chain message handler triggered by relayer-delivered ISMP proofs — with `finalize=true`, meaning it is the sole path to release escrow for an order: [3](#0-2) 

The Tron/legacy variant has the identical pattern using low-level `.call` with `IERC20.transfer.selector`, which still reverts on `TransferFailed` for a paused/blacklisted token, blocking the whole loop: [4](#0-3) 

If any single token in `order.inputs` becomes non-transferable after the order is placed (e.g., issuer pauses transfers, or the beneficiary address is blacklisted by a compliant stablecoin), `safeTransfer`/the low-level call reverts, the entire `onAccept` call reverts, and the relayer's delivery transaction fails. Because there is no partial-token withdrawal function and no retry-with-subset mechanism, none of the escrowed tokens for that order — including perfectly healthy ones bundled alongside the blocked token — can ever be released. This is analogous to the referenced `VE3DRewardPool.getReward()` bug: bundling multiple tokens into a single all-or-nothing transfer loop makes the whole claim/withdrawal permanently DoS'd by one problematic token.

### Impact Explanation
This causes permanent freezing of escrowed user/solver funds for any multi-token order where one input token becomes untransferable (pause, blacklist, sanction freeze) — a realistic and externally-triggerable condition for compliant stablecoins (USDC-style) or any token with an owner-controlled pause/blacklist. Unlike the veToken case (rewards, recoverable via other means), here the funds are the escrowed principal itself: users cannot get inputs back via cancellation either, since `_cancelSameChain`/`_cancelFromSource`/`_cancelFromDest` all ultimately call the same `_withdraw` loop over all remaining tokens, so cancellation is equally blocked. This meets the bar of "permanent freezing of funds" via a route unable to deliver value, satisfying Medium/High severity.

### Likelihood Explanation
Likelihood is moderate: it requires (a) a multi-token order where at least one input is a token capable of pausing/blacklisting transfers, and (b) that token being paused/blacklisted for the beneficiary or globally at settlement time. This is externally triggerable by any third party controlling such a token's compliance mechanism (issuer, sanctions list) and does not require any Hyperbridge-side compromise — it's a reachable condition from ordinary intent flows using widely-used compliant tokens (e.g., USDC has `blacklist`), matching the judged Medium severity of the original finding.

### Recommendation
Decouple per-token transfer from the atomic settlement/refund flow: either (1) allow `_withdraw` to accept a caller-specified subset of tokens to skip an unavailable one and retry with the remainder, (2) wrap each transfer in `try/catch` and, on failure, credit the beneficiary an internal claimable balance for that token instead of reverting the whole loop, or (3) split escrow accounting so each token's release is an independent call rather than one atomic loop across heterogeneous tokens.

### Proof of Concept
1. User places a same-chain or cross-chain order with `order.inputs = [USDC, TOKEN_X]`, escrowing both tokens via `placeOrder`.
2. Before settlement, the issuer of `TOKEN_X` (or USDC) blacklists the order's beneficiary address / pauses transfers.
3. A solver fills the order; the cross-chain `RedeemEscrow` message is dispatched and delivered via `onAccept`, which calls `_withdraw(body, false, true)`.
4. The loop in `_withdraw` reaches `TOKEN_X`'s `IERC20.safeTransfer`, which reverts due to the pause/blacklist.
5. The entire `onAccept` transaction reverts — the relayer's delivery transaction fails, `_orders[commitment][USDC]` is never decremented, and USDC (a perfectly transferable token) remains permanently locked in escrow alongside the frozen `TOKEN_X`, with no available function to withdraw USDC alone.

### Citations

**File:** sdk/packages/core/contracts/apps/IntentGatewayV2.sol (L55-77)
```text
struct Order {
    /// @dev The address of the user who is initiating the transfer
    bytes32 user;
    /// @dev The state machine identifier of the origin chain
    bytes source;
    /// @dev The state machine identifier of the destination chain
    bytes destination;
    /// @dev The block number by which the order must be filled on the destination chain
    uint256 deadline;
    /// @dev The nonce of the order
    uint256 nonce;
    /// @dev Represents the dispatch fees associated with the IntentGateway.
    uint256 fees;
    /// @dev Optional session key used to select winning solver.
    address session;
    /// @dev The predispatch information for the order
    /// This is used to encode any calls before the order is placed
    DispatchInfo predispatch;
    /// @dev The tokens that are escrowed for the filler.
    TokenInfo[] inputs;
    /// @dev The filler output, ie the tokens that the filler will provide
    PaymentInfo output;
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
