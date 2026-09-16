### Title
Single reverting/blacklisting token in a multi-token `WithdrawalRequest` permanently blocks release of all other escrowed tokens - (File: `evm/src/apps/intentsv2/IntentsBase.sol`)

### Summary
`IntentsBase._withdraw` iterates over every token in a `WithdrawalRequest.tokens` array and calls `safeTransfer`/native transfer for each one to release escrowed order funds. Because the loop is not fault-tolerant, a single token that reverts on transfer (e.g. a blacklisting/pausable ERC-20, or one that runs out of liquidity/logic bug) causes the entire `_withdraw` call — and therefore the entire cross-chain `RedeemEscrow`/`RefundEscrow` delivery or GET-response cancellation — to revert, permanently blocking release of the *other*, perfectly healthy tokens escrowed for that same order commitment. This mirrors the EigenLayer finding where one bad strategy in a multi-strategy withdrawal blocks withdrawal of the other strategies' shares.

### Finding Description
`_withdraw` is the single choke point used to release escrow for both successful fills and refunds/cancellations: [1](#0-0) 

It is invoked from `onAccept` when Hyperbridge delivers a `RedeemEscrow`/`RefundEscrow` post request: [2](#0-1) 

and from `onGetResponse` for source-chain cancellation: [3](#0-2) 

An `Order`/`WithdrawalRequest` can escrow multiple input tokens (`order.inputs` is an array of `TokenInfo`), all of which end up in the same `body.tokens` array passed to `_withdraw`. Inside the loop, each token transfer uses `IERC20.safeTransfer`, which reverts the whole transaction on failure: [4](#0-3) 

If any one of those tokens is a malicious/blacklisting/pausable ERC-20 (or simply reverts for a benign reason — paused, out of gas on a hook, contract bug), the `safeTransfer` for that index reverts, unwinding the entire `_withdraw` call. Because `_withdraw` is only reached via `onAccept`/`onGetResponse` (both triggered by relayed Hyperbridge messages), the entire cross-chain message delivery fails. Per the ISMP request handler, when `on_accept` returns an error the just-written request receipt is deleted so the message can be retried: [5](#0-4) 

but retrying does not help if the offending token is permanently frozen/blacklisted/paused — every retry will revert at the exact same index, and there is no mechanism to skip that one token and still release the others (unlike EigenLayer's post-fix `indicesToSkip` pattern). The same unguarded loop-with-safeTransfer/low-level-call pattern also exists in the Tron variant of the contract: [6](#0-5) 

### Impact Explanation
Any order that escrows more than one input token (a very common multi-asset order) is exposed: if one of the input tokens becomes non-transferable (blacklist added by the token issuer, pause, or any other revert condition — no privileged/malicious actor is required, matching the report's later characterization as a possible non-malicious revert), the *entire* escrow for that order — including all the other, unaffected tokens — becomes permanently stuck. There is no partial-release path and no per-token skip mechanism, so unlike the EigenLayer case (where the user could re-queue a withdrawal excluding the bad strategy after some delay), here there is no workaround at all: `_withdraw` is only reachable through the fixed `onAccept`/`onGetResponse` flow and always attempts every token in the same call. This is a permanent freezing-of-funds condition for the healthy tokens in the order, reachable by a single relayed message/order — Medium/High severity depending on frequency of multi-token orders.

### Likelihood Explanation
Multi-input-token orders are a normal, expected use case of the intents system (the `TokenInfo[]` array design explicitly supports this). Tokens with blacklist/pause functionality (e.g., USDC, USDT) are commonly used as intent inputs, and a legitimate blacklist action or pause by the token issuer against the escrow contract, the beneficiary, or globally is a realistic, non-malicious trigger. No attacker privilege is required beyond normal token administration or a bug/liquidity issue in one of the tokens.

### Recommendation
Make `_withdraw` fault-tolerant per token, analogous to EigenLayer's `indicesToSkip` fix: wrap each token transfer in a try/catch (or use a low-level call and record failures) so that a reverting/blacklisted token does not block release of the other tokens in the same `WithdrawalRequest`. Failed transfers should leave that token's escrow balance untouched and emit an event so a later retry (or an explicit sweep/skip function) can attempt to release it once/if the condition clears, without holding the healthy tokens hostage.

### Proof of Concept
1. User places a same-chain or cross-chain order with two input tokens: `TOKEN_A` (healthy) and `TOKEN_B` (a standard ERC-20 that later becomes blacklistable/pausable, e.g. USDC-like).
2. Order is filled or cancelled, triggering `RedeemEscrow`/`RefundEscrow` dispatch, eventually calling `onAccept` → `_withdraw` on the source chain with `body.tokens = [TOKEN_A, TOKEN_B]`.
   - `_withdraw` loop: [4](#0-3) 
3. Before delivery, `TOKEN_B`'s issuer blacklists the beneficiary (or the escrow contract) or pauses transfers.
4. Relayer submits the `RedeemEscrow`/`RefundEscrow` message; `onAccept` → `_withdraw` iterates tokens, successfully transfers `TOKEN_A`... reaches `TOKEN_B`, `safeTransfer` reverts, unwinding the whole call (including the `TOKEN_A` transfer that happened earlier in the same call).
5. Every subsequent retry of the same message hits the same revert on `TOKEN_B`, since it is the same fixed `body.tokens` array and there is no per-token skip — `TOKEN_A`'s escrow (and any fees) remain permanently locked in the contract alongside `TOKEN_B`'s.

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

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L360-366)
```text
    function onGetResponse(IncomingGetResponse calldata incoming) external override onlyHost {
        _checkRelayer(incoming.relayer);
        if (incoming.response.values[0].value.length != 0) revert Filled();

        WithdrawalRequest memory body = abi.decode(incoming.response.request.context, (WithdrawalRequest));
        _withdraw(body, true, true);
    }
```

**File:** modules/ismp/core/src/handlers/request.rs (L122-125)
```rust
				// Delete receipt if module callback failed so it can be timed out
				if res.is_err() {
					host.delete_request_receipt(&wrapped_req)?;
				}
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L691-723)
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

        // redeem tx fees
        uint256 fees = _orders[body.commitment][TRANSACTION_FEES];
        if (fees > 0) {
            address feeToken = IDispatcher(host()).feeToken();
            (bool success,) = feeToken.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, fees));
            if (!success) revert TransferFailed();
            delete _orders[body.commitment][TRANSACTION_FEES];
        }
```
