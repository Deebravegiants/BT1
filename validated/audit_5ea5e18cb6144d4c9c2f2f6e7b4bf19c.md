### Title
Escrow release loop reverts on a single blocklisted/failing token, permanently freezing all escrowed funds in an order - (File: evm/src/apps/intentsv2/IntentsBase.sol)

### Summary
`IntentsBase._withdraw` (used for cross-chain `RedeemEscrow`/`RefundEscrow` fulfillment via `ExtrinsicIntents.onAccept`, and for same-chain fills/cancels via `IntrinsicIntents`) iterates over every token in a `WithdrawalRequest.tokens` array and calls `IERC20.safeTransfer`/`_sendValue` for each one in a single atomic loop. The Tron variant of `IntentGatewayV2.withdraw` has the identical pattern. If any single token's transfer reverts (e.g. a blocklisted USDC/USDT address, a malicious/paused token, or a token that reverts on transfer to a given recipient), the entire withdrawal reverts — mirroring the `sweepTo`/`_liquidate` DOS described in the source report.

### Finding Description
`_withdraw` decrements escrow and transfers out each token in a `for` loop with no isolation between iterations: [1](#0-0) 

This function is invoked from the cross-chain settlement path (`RedeemEscrow`/`RefundEscrow` handled in `onAccept`, which is called permissionlessly by the Hyperbridge host after any relayer delivers a proven POST request) as well as the same-chain fill/cancel paths in `IntrinsicIntents`: [2](#0-1) [3](#0-2) 

An order's `WithdrawalRequest.tokens` list can contain multiple distinct ERC20 inputs (an order can escrow several input tokens at once, as built in `IntentGatewayV2.placeOrder`'s multi-asset input loop): [4](#0-3) 

If one of the escrowed input tokens becomes untransferable to the beneficiary (blocklisted address on a censorable stablecoin, token paused, token with a bugged/malicious `transfer` that reverts under certain conditions), `IERC20(token).safeTransfer(beneficiary, amount)` reverts, which reverts the whole `_withdraw` call — and therefore the whole `fillOrder`, `cancelOrder`, or cross-chain `onAccept`/`onGetResponse` call. The Tron gateway's analogous `withdraw` function has the same all-or-nothing loop over `body.tokens`: [5](#0-4) 

Because `onAccept` is the unsigned/permissionless entrypoint the Hyperbridge host calls after any relayer delivers the message, and because it is the only way to release cross-chain escrow, this single point of failure blocks release of *all* escrowed assets for the order, not just the problematic token.

### Impact Explanation
Once a token in an order's input/output set cannot be transferred to its intended recipient, the entire order's escrow — including all *other*, unaffected tokens and any accrued relayer/protocol fees — becomes permanently stuck:
- The solver/filler cannot redeem escrow for a cross-chain fill (`RedeemEscrow`), so funds already delivered on the destination by the solver are never repaid, and no relayer can ever push a successful `onAccept` past the failing transfer.
- The user cannot cancel/refund an order (`RefundEscrow`, `_cancelSameChain`) to recover their original deposit if one of the multiple escrowed input tokens becomes untransferable.
- Because these are external ERC20 admin actions (freezing/blocklisting) largely outside the protocol's control and potentially permanent, this is a genuine freezing-of-funds condition, not merely a resource/gas DoS. This matches the "permanent freezing of funds" acceptance criterion.

### Likelihood Explanation
Multi-token orders (multiple `TokenInfo` inputs/outputs) are an explicit, supported feature of `IntentGatewayV2`/`IntentsBase`, so orders with more than one distinct ERC20 are a normal occurrence, not an edge case. Common bridged/settled assets (USDC, USDT, and other centrally-administered tokens) implement address blocklisting, and a token issuer freezing either the gateway contract itself or a specific beneficiary address is a realistic, previously-seen event (as cited in the original report). No malicious relayer, governance, or admin action within Hyperbridge is required — the trigger is external to the protocol (the token issuer), and only a single normal cross-chain fill/cancel is needed to encounter it.

### Recommendation
Make per-token transfer failures non-fatal to the rest of the withdrawal:
- Wrap each token transfer in a try/catch (or use low-level `.call` and check success without reverting the batch), and on failure, credit the amount to a separate per-user/per-token "pending withdrawal" balance that can be claimed later or via an alternate recipient once unblocked, instead of reverting the whole loop.
- Alternatively, support partial/itemized settlement: allow `withdraw`/`_withdraw` to skip a single failing token (emitting an event) while still releasing all other tokens and fees, and expose a separate rescue/claim function for skipped tokens.
- Ensure `_filled`/escrow bookkeeping is only marked complete for the tokens actually transferred so a later retry (with a different beneficiary route) remains possible for the stuck token.

### Proof of Concept
1. User places a same-chain order with two input tokens: `inputs[0] = USDC`, `inputs[1] = DAI`, escrowed via `placeOrder` (`evm/src/apps/IntentGatewayV2.sol:228-256`).
2. Order is filled or cancelled, triggering `_withdraw(body, ...)` in `IntentsBase.sol:451-470`, which loops over both tokens.
3. Before settlement, USDC's issuer blocklists the `beneficiary` address (a normal, real-world admin capability of USDC/USDT).
4. `IERC20(USDC).safeTransfer(beneficiary, amount)` reverts inside the loop.
5. The entire `_withdraw` call reverts, so the DAI portion — which had no issue — is also never released, and neither is the accrued relayer fee. The same failure blocks all future retries of `fillOrder`/`cancelOrder`/`onAccept` for this commitment as long as the blocklist stands, permanently freezing the escrow.

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

**File:** evm/src/apps/intentsv2/IntrinsicIntents.sol (L126-136)
```text
        WithdrawalRequest memory body = WithdrawalRequest({
            commitment: commitment, tokens: escrowedInputs, beneficiary: bytes32(uint256(uint160(msg.sender)))
        });
        _withdraw(body, false, isFullyFilled);

        if (isFullyFilled) {
            _execute(order, outputsLen);
            emit OrderFilled({commitment: commitment, filler: msg.sender, outputs: outputFills, inputs: escrowedInputs});
        } else {
            delete _filled[commitment];
            emit PartialFill({commitment: commitment, filler: msg.sender, outputs: outputFills, inputs: escrowedInputs});
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
