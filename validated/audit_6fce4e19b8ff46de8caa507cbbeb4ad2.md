### Title
Malicious/reverting ERC20 in a multi-token order permanently freezes escrow and griefs solvers (all-or-nothing `_withdraw` loop) - (File: `evm/src/apps/intentsv2/IntentsBase.sol`)

### Summary
`IntentGatewayV2.placeOrder` accepts an arbitrary list of `order.inputs` tokens with no whitelist check [1](#0-0) . Escrow release/refund for those tokens is done in `_withdraw`, which iterates the full token list and calls `IERC20(token).safeTransfer` for each entry, reverting the entire call if any single transfer reverts [2](#0-1) . Because this is a push-based, all-or-nothing loop over caller-chosen tokens (same bug class as the OpenQ report), one malicious token in a multi-input order can permanently DoS the release of every other (legitimate) token bundled in that same order/commitment.

### Finding Description
`placeOrder` lets the order creator specify any ERC20 address as an input token with no allow-list or transfer-safety check [3](#0-2) . Multiple distinct input tokens can be escrowed under the same `commitment` [4](#0-3) .

Escrow is released via `_withdraw`, shared by same-chain fill (`_fillSameChain`), same-chain cancel (`_cancelSameChain`), and cross-chain `RedeemEscrow`/`RefundEscrow` delivery (`onAccept`)/`onGetResponse`:
```solidity
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
``` [5](#0-4) 

If any one `token` in `body.tokens` is a malicious ERC20 that reverts on transfer (or a token that can be intentionally blacklisted/paused against the gateway or beneficiary), the entire `_withdraw` call reverts. There is no per-token try/catch or pull-based fallback, so the escrow accounting for every *other* token in the same order is stuck: `_orders[commitment][token]` for the legitimate tokens is never decremented and can never be swept out, because the same `_withdraw` path is the only way to release them.

The cross-chain "fill" path (`_fillCrossChain` → dispatched `RedeemEscrow` handled by `onAccept`) is the most damaging: a solver observes the order, delivers the requested output tokens directly to the beneficiary on the destination chain (irreversible), and only afterward does the source chain process the `RedeemEscrow` message to release the solver's earned input tokens via `_withdraw` [6](#0-5) . If the order creator included one legitimate token (e.g., USDC) plus one malicious revert-on-transfer token as inputs, the solver has already paid out the outputs before discovering that `_withdraw` can never succeed — permanently freezing the solver's legitimate USDC payment (and the malicious token) in escrow. The same all-or-nothing failure applies to `_cancelSameChain`/`RefundEscrow`, which can trap a user's own legitimate refund behind one bad token, and to `Execute`'s replayable `_requestCommitments`/`onAccept` retry semantics not being available here since `_withdraw` has no retry/partial-success path.

The Tron variant (`evm/tron/contracts/apps/IntentGatewayV2.sol`) has the identical pattern in its `withdraw` function, using a low-level `.call` that still explicitly reverts the whole transaction via `revert TransferFailed()` on any single token failure [7](#0-6) .

### Impact Explanation
This is a permanent freezing-of-funds bug reachable by any unprivileged user who calls `placeOrder` with a crafted multi-token input list — no admin/governance privilege needed. It can be used to:
- Grief solvers: a solver fills a cross-chain order believing they'll be repaid in escrowed inputs, but the malicious token bundled by the order creator makes `RedeemEscrow` permanently revert, freezing the solver's legitimately earned tokens forever.
- Freeze a user's own escrow (self-inflicted, lower severity) or, more importantly, freeze funds shared with counterparties (solver payouts) that the malicious actor does not own but can hold hostage.

This meets the "permanent freezing of funds" bar for High severity, matching the referenced report's bug class exactly, since Hyperbridge's IntentGatewayV2 also uses a push-based, all-or-nothing loop over externally chosen ERC20s with no per-token isolation or pull-based fallback.

### Likelihood Explanation
Likelihood is High: creating a malicious ERC20 that reverts on transfer (e.g., only allowing transfers from an allow-listed sender, or one that can be paused/blacklisted post-escrow) is trivial and requires no special access. Any user can call `placeOrder` and bundle such a token alongside a legitimate one; no whitelist or token-safety validation exists in `placeOrder` or `_withdraw` to prevent this.

### Recommendation
- Do not perform an all-or-nothing loop over externally supplied tokens when releasing escrow. Isolate each token's transfer (e.g., wrap each `safeTransfer` in a try/catch, or use a low-level call and only mark that specific token's escrow row as pending/failed rather than reverting the whole `_withdraw`).
- Provide a per-token, permissionless "sweep failed transfer" / pull-based rescue path so a beneficiary can still claim the successfully-transferable tokens even when one token in the same order is malicious.
- Alternatively, restrict `order.inputs`/`order.output.assets` tokens to a governance-maintained allow-list before escrow is accepted, consistent with the recommendation in the referenced report.

### Proof of Concept
1. Deploy a malicious ERC20 `EvilToken` whose `transfer`/`transferFrom` reverts unless `msg.sender` is an allow-listed address (attacker-controlled).
2. Attacker calls `placeOrder` with `order.inputs = [ {token: USDC, amount: 1000e6}, {token: EvilToken, amount: 1} ]`, escrowing both under the same `commitment` (`evm/src/apps/IntentGatewayV2.sol:194-373`).
3. A solver on the destination chain fills the order (cross-chain), delivering the requested output tokens directly to the beneficiary — this transfer is irreversible.
4. Once the fill message reaches the source chain, `onAccept` dispatches `RedeemEscrow` → `_withdraw(body, false, true)` iterates `[USDC, EvilToken]` (`evm/src/apps/intentsv2/IntentsBase.sol:451-470`). The `EvilToken.transfer` call reverts, causing the entire `_withdraw` transaction to revert.
5. Because the source-chain host has no retry/partial mechanism for this delivered message beyond re-attempting the identical call, the solver's USDC payout (and the EvilToken) remain locked in `_orders[commitment]` forever — the solver already paid the output tokens and cannot recover the input escrow.

### Citations

**File:** evm/src/apps/IntentGatewayV2.sol (L194-230)
```text
    function placeOrder(Order memory order, bytes32 graffiti) public payable nonReentrant {
        if (order.inputs.length == 0) revert InvalidInput();

        // Reject duplicate output tokens
        uint256 outputsLen_ = order.output.assets.length;
        for (uint256 i; i < outputsLen_;) {
            bytes32 token = order.output.assets[i].token;
            assembly ("memory-safe") {
                if tload(token) {
                    mstore(0, 0xb4fa3fb3) // InvalidInput.selector
                    revert(0x1c, 0x04)
                }
                tstore(token, 1)
            }
            unchecked {
                ++i;
            }
        }
        // Clean up transient storage so repeated placeOrder calls in the same tx don't false-positive.
        for (uint256 i; i < outputsLen_;) {
            bytes32 token = order.output.assets[i].token;
            assembly ("memory-safe") {
                tstore(token, 0)
            }
            unchecked {
                ++i;
            }
        }

        address hostAddr = host();
        order.user = bytes32(uint256(uint160(msg.sender)));
        order.source = IDispatcher(hostAddr).host();
        order.nonce = _nonce++;

        uint256 inputsLen = order.inputs.length;

        // Phase 1: Transfer tokens and record actual received amounts.
```

**File:** evm/src/apps/IntentGatewayV2.sol (L313-328)
```text
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

**File:** evm/src/apps/IntentGatewayV2.sol (L364-373)
```text
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
