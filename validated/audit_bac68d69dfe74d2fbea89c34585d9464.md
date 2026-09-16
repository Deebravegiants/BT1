### Title
Intent solver can permanently freeze a filled order's escrowed input tokens by redeeming to a blocklist-capable-token-blocked address - ([File: evm/src/apps/intentsv2/IntentsBase.sol])

### Summary
`IntentsBase._withdraw` unconditionally "pushes" escrowed ERC-20 tokens to a `beneficiary` address decoded from a cross-chain `WithdrawalRequest`, exactly like the `LienToken#_getPayee`/`_payment` push-payment pattern in the referenced Astaria finding. For cross-chain fills, the beneficiary of the `RedeemEscrow` payout is `msg.sender` of the solver who called `fillOrder` on the destination chain, embedded into the dispatched message body at fill time. If that solver address is (or later becomes) a blocked address for the escrowed ERC-20 (e.g. USDC/USDT blocklist), the `safeTransfer` in `_withdraw` reverts every time delivery is attempted, permanently freezing the user's escrowed input tokens with no way to redirect the payout.

### Finding Description
`IntentsBase._withdraw` performs an unconditional push transfer to an address taken from message data: [1](#0-0) 

The `beneficiary` here comes straight from `WithdrawalRequest.beneficiary`, decoded from an ISMP message body. For the cross-chain fill path, `ExtrinsicIntents._fillCrossChain` builds this beneficiary as the filler's own `msg.sender` and dispatches it back to the source chain to redeem the escrow: [2](#0-1) 

When the `RedeemEscrow` message is delivered on the source chain, `onAccept` decodes the body and calls `_withdraw`, which does `IERC20(token).safeTransfer(beneficiary, amount)`. This is a "push" rather than a "pull" payment: the recipient address is baked into the ISMP message at fill time and can never be changed on retry. `EvmHost.dispatchIncoming(PostRequest, address relayer)` isolates delivery failures per-message (deletes the receipt so the message can be retried) rather than reverting the whole batch: [3](#0-2) 

but retrying does not help here because the message body — and therefore the target `beneficiary` — is fixed and immutable. If that address is on an ERC-20 issuer's blocklist (or is any contract that unconditionally reverts on `transfer`), every redelivery attempt of that specific commitment will fail identically, forever.

An intent solver can trigger this in a single transaction: call `fillOrder`/`_fillCrossChain` from an address they know is (or will become) blocklisted for the order's input token, pay the required output tokens to the user's beneficiary (satisfying the swap for the user), and dispatch the `RedeemEscrow` request. Once relayed, `_withdraw`'s push transfer to the solver's own blocklisted address will permanently revert, locking the user's originally escrowed input tokens in the `IntentGatewayV2`/`ExtrinsicIntents` contract on the source chain with no recovery mechanism — `_filled[commitment]` is already set, so no one else can ever claim that escrow.

### Impact Explanation
This meets the "permanent freezing of funds" bar: the escrowed input tokens for that order become permanently unredeemable once `_filled[commitment]` is set and the sole valid beneficiary (the filler) cannot receive the token. Unlike the original LienToken report (where the attacker profits by seizing collateral), here the loss is that principal capital becomes dead weight stuck in the gateway contract — a permanent freeze rather than direct theft, but it satisfies the finding's own root cause: irrevocably pushing payment to an attacker-influenced address decoded from a message, embedded before delivery and non-retriable with a different recipient. The scope of loss is bounded per order (the escrowed input amount), but it is fully attacker-controllable and repeatable across many orders, and the escrow can never be un-frozen through any exposed function.

### Likelihood Explanation
Likelihood is moderate: the attacker (acting as an intent solver) must control or acquire an address later blocklisted by the relevant ERC-20 issuer (e.g., self-report to Circle/Tether, or use a sanctioned address), and must be willing to pay the legitimate output amount to the user to fill the order. This is a deliberate, self-funded griefing action rather than a passive bug trigger, so it is less likely to occur accidentally, but it is straightforward and cheap for a determined attacker to execute against any order using a blocklist-capable ERC-20 as an input asset, and requires only a single `fillOrder` transaction plus the resulting message delivery.

### Recommendation
Avoid unconditional "push" transfers of arbitrary/attacker-influenced recipients baked into cross-chain messages. Options:
- Switch `_withdraw`'s payout to a pull-based claim (escrow release into an internal balance mapping keyed by beneficiary, with a separate `claim()` function the beneficiary calls), so a blocked beneficiary cannot brick the whole redemption and cannot lock other parties' funds.
- Wrap the token transfer in `_withdraw` in a try/catch (or low-level call) and, on failure, retain the funds in a recoverable/claimable state (e.g., allow governance or the original order owner to redirect/rescue) instead of leaving the commitment permanently unretriable.
- Maintain an allowlist of well-behaved ERC-20s eligible as intent inputs/outputs, excluding tokens with issuer-controlled blocklists.

### Proof of Concept
1. User places a cross-chain order (`Order`) with `input = [USDC, amount]` on chain A via `IntrinsicIntents`/`placeOrder`, escrowing USDC in the gateway contract.
2. Attacker, using an address `E` that Circle will imminently blocklist (or already controls a blocklisted contract), calls `fillOrder` on chain B (`ExtrinsicIntents._fillCrossChain`), providing the required output tokens to the order's beneficiary — the swap for the legitimate user completes normally.
3. `_fillCrossChain` sets `_filled[commitment] = E` and dispatches a `RedeemEscrow` `WithdrawalRequest{beneficiary: E, tokens: [USDC, amount]}` back to chain A (`ExtrinsicIntents.sol` lines 164-219).
4. Circle blocklists `E` for USDC (or `E` is a contract engineered to always revert on `transfer`).
5. When the ISMP relayer delivers the `RedeemEscrow` message, `EvmHost.dispatchIncoming` calls `onAccept` → `_withdraw`, which executes `IERC20(USDC).safeTransfer(E, amount)` (`IntentsBase.sol` lines 451-470) and reverts.
6. `EvmHost.dispatchIncoming` catches the failure and deletes the receipt so it can be retried, but the message body (and thus `beneficiary = E`) never changes — every retry fails identically, and since `_filled[commitment]` is already set to `E`, no alternate party can ever claim the escrow. The user's original USDC input remains permanently locked in the gateway contract on chain A.

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

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L164-219)
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
            nativeFee
        );

        // Refund any unspent native tokens to the solver.
        if (msgValue > 0) {
            _sendValue(msg.sender, msgValue);
        }

        emit OrderFilled({commitment: commitment, filler: msg.sender, outputs: outputFills, inputs: order.inputs});
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
