Based on the investigation, there is a valid analog rooted in the intents escrow release logic.

### Title
Pausable Token in a Multi-Asset Order Permanently Freezes All Escrowed Funds for That Order - ([File: evm/src/apps/intentsv2/IntentsBase.sol])

### Summary
`_withdraw` releases every escrowed token for an order commitment in a single atomic loop using `safeTransfer`. If any one of the escrowed input tokens is a pausable ERC20 (e.g. BNB-peg, ZIL-like tokens, or any centrally-pausable stablecoin) and gets paused by its issuer, the transfer for that single token reverts and reverts the entire withdrawal — permanently freezing the *other*, unaffected tokens escrowed in the same order, plus the accumulated transaction fees, with no way to partially recover or retry.

### Finding Description
`_withdraw` in `IntentsBase.sol` is the shared release path for both cross-chain settlement (`onAccept` handling a `RedeemEscrow`/`WithdrawalRequest`) and same-chain fills/cancellations (`IntrinsicIntents._cancelSameChain`, `IntrinsicIntents.fillOrder`). It iterates `body.tokens` and unconditionally calls `IERC20(token).safeTransfer(beneficiary, amount)` for every token in the array, then — only if `finalize` is true — forwards the accumulated fee-token balance: [1](#0-0) [2](#0-1) 

An order can escrow multiple input tokens simultaneously (`placeOrder` accepts an `order.inputs` array of arbitrary ERC20s with no allow-list check): [3](#0-2) [4](#0-3) 

If any one of those input tokens is later paused by its own admin (an external, unprivileged-to-Hyperbridge event, exactly the bug class in the report — pausable ERC20 blocking a mandatory transfer), the `safeTransfer` call for that token in `_withdraw`'s loop reverts. Because the loop is not isolated per-token (no try/catch, no per-token accounting that can be skipped), the revert bubbles up and reverts the whole `_withdraw` call — including the release of every *other* healthy escrowed token and the fee-token payout for that commitment.

For the cross-chain case, this call is reached from `onAccept`, which is invoked by the ISMP host after a relayer has already proven and delivered the `RedeemEscrow` message on-chain. Since the message body (and thus the exact token list) is fixed once dispatched, and there is no alternate/partial-withdrawal entry point for a `finalize`d order, the same revert occurs on every re-delivery attempt — the settlement can never succeed, and both the solver's earned inputs and the order's fee-token remain permanently locked in the contract.

For the same-chain refund case (`cancelOrder` → `_cancelSameChain` → `_withdraw` with `isRefund=true`), a user who escrowed several input tokens for one order loses access to *all* of them — not just the paused one — the moment any single input token is paused, since `_withdraw` refunds the full remaining token set in one atomic call: [5](#0-4) 

### Impact Explanation
This is a permanent freezing-of-funds bug reachable by an ordinary user simply placing a multi-input order that includes a token which is later paused by its issuer (no privileged Hyperbridge action required). Once paused:
- All co-escrowed tokens (non-paused ones) and accrued protocol/solver fees for that specific order become permanently unrecoverable, because release is bundled atomically per commitment.
- For cross-chain orders, the already-delivered `RedeemEscrow` settlement message can never be finalized, effectively bricking that message/order permanently on the source chain.

### Likelihood Explanation
Likelihood is realistic but conditional: it requires (a) an order/escrow containing at least one third-party token that is administratively pausable, and (b) that token being paused while funds are still escrowed. Given Hyperbridge's intents system accepts arbitrary ERC20s as inputs with no token allow-list, and many real-world stablecoins/wrapped assets (USDC, USDT, BUSD-style tokens) implement pausability, this is a plausible operational scenario rather than a contrived edge case.

### Recommendation
Isolate per-token transfer failures in `_withdraw` (e.g., low-level `call` + best-effort accounting that lets a paused token's balance remain claimable later while releasing the rest immediately), or maintain an allow-list/registry that excludes tokens with owner-controlled pause functionality from being used as escrowed order inputs. At minimum, decouple fee-token payout and each input-token transfer into independently retryable/claimable steps instead of one atomic loop gating all releases for a commitment.

### Proof of Concept
1. User places a same-chain order via `placeOrder` with two inputs: `USDC` and `PausableToken` (a third-party ERC20 with owner `pause()`), escrowing both into `_orders[commitment]`.
2. Before the order is filled or cancelled, `PausableToken`'s owner calls `pause()`.
3. User calls `cancelOrder` to refund; `_cancelSameChain` builds `remainingTokens` for both `USDC` and `PausableToken` and calls `_withdraw`.
4. `_withdraw`'s loop reaches `IERC20(PausableToken).safeTransfer(...)`, which reverts because the token is paused.
5. The entire `_withdraw` call reverts, so the `USDC` refund that would otherwise have succeeded is also blocked — both tokens remain stuck in escrow indefinitely, with no partial-refund path available. [6](#0-5)

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

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L472-477)
```text
        if (finalize) {
            uint256 fees = _orders[body.commitment][TRANSACTION_FEES];
            if (fees > 0) {
                delete _orders[body.commitment][TRANSACTION_FEES];
                IERC20(IDispatcher(host()).feeToken()).safeTransfer(beneficiary, fees);
            }
```

**File:** evm/src/apps/IntentGatewayV2.sol (L228-234)
```text
        uint256 inputsLen = order.inputs.length;

        // Phase 1: Transfer tokens and record actual received amounts.
        // For fee-on-transfer tokens, the gateway receives less than the requested amount.
        // We mutate order.inputs to reflect actual received so the commitment and escrow
        // are consistent with what the gateway holds.
        uint256 msgValue = msg.value;
```

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
