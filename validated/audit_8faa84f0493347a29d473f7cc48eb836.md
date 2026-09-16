## Title
Permanent freeze of Intent Gateway escrow when the withdrawal beneficiary is a blacklisted address (e.g., USDC/USDT) - (`evm/src/apps/intentsv2/IntentsBase.sol`)

### Summary
`IntentsBase._withdraw`, the single settlement path used by both `RedeemEscrow` and `RefundEscrow` handling in the IntentGateway, pushes escrowed ERC-20 tokens directly to a `beneficiary` address that is baked immutably into the cross-chain `WithdrawalRequest` body. If that token enforces an address blacklist (USDC/USDT-style) and the beneficiary is or becomes blacklisted, every delivery attempt of the settlement message reverts, permanently locking the escrowed funds with no pull-based fallback or rescue path — the same root cause as the referenced Cooler.sol finding (push-only repayment to a potentially blacklisted address with no alternative claim mechanism).

### Finding Description
`_withdraw` loops over the withdrawal request's token list and unconditionally does a push transfer to `beneficiary`: [1](#0-0) 

```solidity
function _withdraw(WithdrawalRequest memory body, bool isRefund, bool finalize) internal {
    address beneficiary = address(uint160(uint256(body.beneficiary)));
    if (finalize) _filled[body.commitment] = beneficiary;
    ...
    IERC20(token).safeTransfer(beneficiary, amount);
``` [2](#0-1) 

This function is reached from `onAccept` for two message kinds:
- **RedeemEscrow** — after a solver fills a cross-chain order on the destination chain (`_fillCrossChain` in `ExtrinsicIntents.sol`), a `RedeemEscrow` message is dispatched back to the source chain with `beneficiary = msg.sender` (the solver), fixed at fill time. [3](#0-2) 
- **RefundEscrow** — after `cancelOrder()` on the destination chain (permissionless for anyone once `order.deadline` has passed), a `RefundEscrow` message is dispatched back with `beneficiary = order.user`.

Delivery of these ISMP requests goes through `EvmHost.dispatchIncoming(PostRequest, relayer)`, which invokes `onAccept` via a low-level `.call`. If that call reverts (e.g., the ERC-20 `transfer` inside `_withdraw` reverts because the beneficiary is blacklisted), the host only deletes the request receipt "so it can be retried": [4](#0-3) 

The retry mechanism assumes a transient failure. But here the beneficiary address is permanently embedded in the message body (it was fixed by the solver's `msg.sender` at fill time or by `order.user` at order-placement time) — there is no way to change it, and no alternate pull-based claim path exists anywhere in `IntentsBase`/`ExtrinsicIntents`/`IntrinsicIntents`. Every retry will fail identically forever. No owner/admin sweep function exists for stuck per-order escrow (the only sweep path, `_execute`'s calldata-dust sweep, is for protocol dust, not stuck order escrow).

### Impact Explanation
This permanently freezes value with no recovery path:
- For **RedeemEscrow**: a solver has already irrevocably delivered real output tokens to the user on the destination chain before the settlement message is even dispatched. If the solver's own settlement address is/becomes blacklisted for the escrowed input token (a stablecoin such as USDC/USDT is a realistic and common escrow asset for intents), the solver's earned collateral is permanently trapped in the source-chain gateway with no way to redirect or reclaim it.
- For **RefundEscrow**: once `cancelOrder()` finalizes on the destination chain, the only path back to the user is this same push transfer; a blacklisted `order.user` address permanently locks the refund escrow.

This matches the required impact bar of "concrete theft or permanent freezing of funds" via an unrecoverable settlement path reachable from ordinary intents/order-fill flow.

### Likelihood Explanation
Reaching the vulnerable code requires no special privilege: any user can place an order denominated in a blacklist-capable token (USDC/USDT are widely used and natural choices for intents), and any solver can fill it or any party can trigger the permissionless post-deadline cancellation. The only external dependency is that the beneficiary address end up on the token issuer's blacklist (a documented, real-world mechanism for USDC/USDT), which is the same assumption underlying the referenced analog report.

### Recommendation
Do not let a single failed push-transfer roll back the entire withdrawal/finalize state, and provide a pull-based fallback:
- Wrap each token transfer with a try/catch (or use `Address.functionCall` with limited gas) and, on failure, credit the amount to an internal "claimable" balance for the beneficiary instead of reverting the whole `_withdraw`.
- Add a permissionless `claim(token, to)` function allowing the beneficiary (or beneficiary-designated address) to pull previously-failed amounts, decoupling delivery success from the beneficiary's ability to receive the specific token.
- Ensure `_filled`/escrow accounting is still finalized (order marked settled) even when a specific leg's push fails, so only the stuck token amount — not the whole settlement — is affected.

### Proof of Concept
1. User places a cross-chain order on chain A with `order.inputs = [USDC]`, escrowing USDC in the gateway.
2. A solver fills the order on chain B (`_fillCrossChain`), delivering the required output tokens to the user; `RedeemEscrow{beneficiary: solver}` is dispatched back to chain A.
3. Before the message is relayed and delivered, the solver's address is added to USDC's blacklist (via Circle or by the attacker orchestrating a report against the solver).
4. The relayer submits the proof; `EvmHost.dispatchIncoming` calls `IntentGatewayV2.onAccept` → `_withdraw` → `IERC20(USDC).safeTransfer(solver, amount)` reverts.
5. `EvmHost.dispatchIncoming` deletes the request receipt to permit "retry," but every subsequent delivery attempt with the same immutable `beneficiary = solver` reverts identically.
6. The escrowed USDC is permanently stuck in the gateway; the solver has already parted with the output tokens on chain B with no way to ever redeem the input escrow, and no rescue function exists to move the funds to a different address. [5](#0-4) [6](#0-5)

### Citations

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L451-485)
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

        if (finalize) {
            uint256 fees = _orders[body.commitment][TRANSACTION_FEES];
            if (fees > 0) {
                delete _orders[body.commitment][TRANSACTION_FEES];
                IERC20(IDispatcher(host()).feeToken()).safeTransfer(beneficiary, fees);
            }

            if (isRefund) {
                emit EscrowRefunded({commitment: body.commitment, tokens: body.tokens});
            } else {
                emit EscrowReleased({commitment: body.commitment, tokens: body.tokens});
            }
        }
    }
```

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L164-210)
```text
    function _fillCrossChain(Order calldata order, FillOptions calldata options, bytes32 commitment) internal {
        uint256 outputsLen = order.output.assets.length;

        _filled[commitment] = msg.sender;

        uint256 msgValue = msg.value;
        address beneficiary = address(uint160(uint256(order.output.beneficiary)));
        TokenInfo[] memory outputFills = new TokenInfo[](outputsLen);

        for (uint256 i; i < outputsLen; i++) {
            bytes32 outputToken = order.output.assets[i].token;
            if (options.outputs[i].token != outputToken) revert InvalidInput();

            address token = address(uint160(uint256(outputToken)));
            uint256 totalRequired = order.output.assets[i].amount;
            uint256 solverAmount = options.outputs[i].amount;

            if (solverAmount < totalRequired) revert InvalidInput();

            (uint256 protocolShare, uint256 beneficiaryShare) =
                _splitSurplus(solverAmount - totalRequired, order.output.call.length > 0);

            if (token == address(0)) {
                if (msgValue < solverAmount) revert InsufficientNativeToken();
                uint256 beneficiaryTotal = totalRequired + beneficiaryShare;
                _sendValue(beneficiary, beneficiaryTotal);
                msgValue -= (beneficiaryTotal + protocolShare);
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
```

**File:** evm/src/core/EvmHost.sol (L794-818)
```text
    function dispatchIncoming(PostRequest memory request, address relayer) external restrict(_hostParams.handler) {
        address destination = _bytesToAddress(request.to);
        uint256 size;
        assembly {
            size := extcodesize(destination)
        }
        if (size == 0) {
            // instead of reverting the entire batch, early return here.
            return;
        }

        // replay protection
        bytes32 commitment = request.hash();
        _requestReceipts[commitment] = relayer;

        (bool success,) = address(destination)
            .call(abi.encodeWithSelector(IApp.onAccept.selector, IncomingPostRequest(request, relayer)));

        if (!success) {
            // so that it can be retried
            delete _requestReceipts[commitment];
            return;
        }
        emit PostRequestHandled({commitment: commitment, relayer: relayer});
    }
```
