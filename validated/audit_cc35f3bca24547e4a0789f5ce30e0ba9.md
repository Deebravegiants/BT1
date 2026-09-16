### Title
Flat, chain-agnostic `RELAYER_MESSAGE_GAS` / `REFUND_POST_GAS` budgets can underprice cross-chain escrow-release messages, stranding solver and cancellation dispatches - ([File: sdk/packages/sdk/src/protocols/intents/GasEstimator.ts])

### Summary
The Intents SDK prices the relayer fee for the cross-chain `RedeemEscrow`/`RefundEscrow`/GET-response settlement messages using flat, hardcoded gas constants (`RELAYER_MESSAGE_GAS`, `SOURCE_GET_RESPONSE_GAS`, `REFUND_POST_GAS`) instead of a live, chain-specific gas estimate. Because different destination chains have materially different proof-verification/consensus costs and L1 data-availability costs, a flat budget can systematically underprice the relayer fee on expensive chains, leaving the settlement message permanently unattractive to relayers and the corresponding escrow stuck.

### Finding Description
`GasEstimator.ts` prices the relayer fee for the cross-chain `RedeemEscrow` POST (dispatched by `_fillCrossChain` in `ExtrinsicIntents.sol`/`IntentGatewayV2.sol` to release source-chain escrow to the filler) using a hardcoded constant instead of a measured estimate: [1](#0-0) 

The code comment explicitly documents that this is a known shortcut and that "a flat number can't track per-chain differences like L1 data costs" — acknowledging the exact class of bug from the report (destination-chain gas requirements and message-dependent costs are not modeled): [2](#0-1) 

The same flat-budget pattern is used for order cancellation refunds: [3](#0-2) 

This flat gas figure is then converted into the actual `relayerFee`/`order.fees` value the filler pays and dispatches on-chain: [4](#0-3) 

`_fillCrossChain` marks the order filled on the destination chain and dispatches the `RedeemEscrow` message with this potentially-underpriced fee, while the source-chain escrow remains locked until that message is delivered and processed by `onAccept`: [5](#0-4) [6](#0-5) 

Critically, once an order is filled on the destination, source-side cancellation is blocked: `onGetResponse` reverts with `Filled()` if the destination's `_filled` slot is non-empty, so the escrow cannot be recovered via the cancellation path either: [7](#0-6) 

Because `DispatchPost.timeout` is set to `0` (no timeout) for these settlement messages, an underpriced message never expires and never becomes eligible for a timeout-based refund path either — it simply sits undelivered indefinitely unless someone notices and manually tops up the fee via `IDispatcher.fundRequest`.

### Impact Explanation
If the flat `RELAYER_MESSAGE_GAS`/`REFUND_POST_GAS` budget underestimates the true cost of delivering and executing `handlePostRequests` on a given source/destination chain (e.g., an expensive L1 like Ethereum mainnet, or a chain with higher consensus-proof verification costs than assumed), no relayer is economically incentivized to deliver the `RedeemEscrow`/refund message. Since:
1. The order is already marked filled on the destination (blocking GET-based cancellation via the `Filled()` revert), and
2. The message carries no timeout (so no automatic refund path triggers),

the escrowed input funds on the source chain become stuck pending manual intervention (an unprivileged `fundRequest` top-up), which an average user/filler has no visibility into. This matches the report's "route unable to deliver messages" / freezing-of-funds pattern, reachable directly from a normal `fillOrder`/`quoteOrderFees` flow using default SDK pricing.

### Likelihood Explanation
Likelihood is Medium: it requires that the flat 1,000,000 gas budget be genuinely insufficient for the destination/source pairing used to price the message (plausible on expensive L1s or chains with unusually costly consensus verification, and explicitly acknowledged as an unmodeled risk in the code's own TODO comment). It does not require any malicious actor — normal usage of the default SDK fee quoting is sufficient to trigger it.

### Recommendation
Replace the flat `RELAYER_MESSAGE_GAS`/`SOURCE_GET_RESPONSE_GAS`/`REFUND_POST_GAS` constants with a measured, per-chain gas estimate (as the TODO in `GasEstimator.ts` already proposes, mirroring the `TokenGateway.quoteNative` pattern that calls `EvmChain.estimateGas` for a reconstructed `handlePostRequests` simulation plus consensus-verification overhead). Additionally, consider setting a bounded, non-zero timeout on these settlement dispatches with an automatic refund/retry path, and surfacing a clear SDK/UI mechanism (or automatic monitoring) to call `fundRequest` when a message is underpriced, so escrow release isn't left solely to manual, unprompted recovery.

### Proof of Concept
1. Filler calls `IntentGateway.quoteOrderFees` for a cross-chain order whose destination or settlement path is on a chain that requires materially more than 1,000,000 gas + the flat consensus/state-proof assumptions baked into `RELAYER_MESSAGE_GAS` (e.g., mainnet Ethereum with high L1 data costs).
2. Filler fills the order via `_fillCrossChain`, which dispatches the `RedeemEscrow` POST with `options.relayerFee` derived from the underestimated flat budget — see `_post`/`_fillCrossChain` in `evm/src/apps/intentsv2/ExtrinsicIntents.sol`.
3. No relayer picks up the message because the fee doesn't cover the real gas cost of `handlePostRequests` + consensus verification on the source chain.
4. Because `order._filled` is already set to true on the destination (line 167 in `_fillCrossChain`), an attempt to cancel from the source via `_cancelFromSource`/`onGetResponse` reverts with `Filled()` — see lines 352-367 of `ExtrinsicIntents.sol`.
5. The source-chain escrow (`_orders[commitment][token]`) remains locked indefinitely until someone manually calls `IDispatcher.fundRequest` to top up the fee — a step neither the SDK nor the contract prompts automatically.

### Citations

**File:** sdk/packages/sdk/src/protocols/intents/GasEstimator.ts (L40-56)
```typescript
/**
 * Gas budget assumed for delivering and executing the cross-chain RedeemEscrow
 * POST message on the SOURCE chain (the message a cross-chain `fillOrder`
 * dispatches back to release escrow to the filler). The relayer fee carried by
 * that dispatch — and the amount a filler's `order.fees` must cover — is this
 * gas priced on the source chain. Sized conservatively so the relayer is
 * reliably incentivised to deliver.
 *
 * TODO: replace this flat budget with a measured estimate via
 * `EvmChain.estimateGas(postRequest)` (a `handlePostRequests` simulation plus
 * its ~600k consensus-verification adder, as the TokenGateway flow does) —
 * the RedeemEscrow postRequest would need to be reconstructed in
 * `estimateCrossChainFees` (`constructRedeemEscrowRequestBody` + host nonce),
 * as the native-dispatch removal deleted that plumbing. A flat number can't
 * track per-chain differences like L1 data costs.
 */
export const RELAYER_MESSAGE_GAS = 1_000_000n
```

**File:** sdk/packages/sdk/src/protocols/intents/GasEstimator.ts (L413-429)
```typescript
	private async estimateCrossChainFees(
		sourceFeeToken: { address: HexString; decimals: number },
		destFeeToken: { address: HexString; decimals: number },
		sourceChainId: string,
		orderFeeGasPriceBumpPercent: bigint,
	): Promise<{ postRequestFee: bigint; relayerFeeInSourceFeeToken: bigint }> {
		// RELAYER_MESSAGE_GAS (1M) already carries generous gas-unit headroom.
		// Direct solver estimates price it at the live gas price, while SDK order
		// quotes explicitly opt into gas-price headroom through the pricing policy.
		const postRequestFeeInSourceFeeToken = await convertGasToFeeToken(
			this.ctx,
			RELAYER_MESSAGE_GAS,
			"source",
			sourceChainId,
			undefined,
			orderFeeGasPriceBumpPercent,
		)
```

**File:** sdk/packages/sdk/src/protocols/intents/OrderCanceller.ts (L48-54)
```typescript
export class OrderCanceller {
	private static readonly DEFAULT_MAX_RECOVERY_RESTARTS = 1
	private static readonly PROOF_FRESHNESS_MAX_RETRIES = 3
	private static readonly PROOF_FRESHNESS_BACKOFF_MS = 500
	/** Gas budgets used to price cancellation delivery on the source chain. */
	private static readonly SOURCE_GET_RESPONSE_GAS = 1_000_000n
	private static readonly REFUND_POST_GAS = 1_000_000n
```

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L126-142)
```text
    /// @dev Posts `body` to the gateway on the order's source chain, paying `nativeFee` in native
    /// tokens when non-zero and in the fee token otherwise.
    function _post(Order calldata order, bytes memory body, uint256 relayerFee, uint256 nativeFee) internal {
        DispatchPost memory request = DispatchPost({
            dest: order.source,
            to: abi.encodePacked(_instance(order.source)),
            body: body,
            timeout: 0,
            fee: relayerFee,
            payer: msg.sender
        });
        if (nativeFee > 0) {
            IDispatcher(host()).dispatch{value: nativeFee}(request);
        } else {
            dispatchWithFeeToken(request);
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

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L352-367)
```text
    /**
     * @dev Handles the response to a Hyperbridge GET request dispatched during
     * `_cancelFromSource`. Verifies that the `_filled` storage slot on the destination
     * chain is empty (meaning the order was never filled), then refunds the escrowed
     * tokens to the original user. Reverts with `Filled` if the slot is non-empty.
     *
     * @param incoming The incoming GET response from Hyperbridge containing the storage proof.
     */
    function onGetResponse(IncomingGetResponse calldata incoming) external override onlyHost {
        _checkRelayer(incoming.relayer);
        if (incoming.response.values[0].value.length != 0) revert Filled();

        WithdrawalRequest memory body = abi.decode(incoming.response.request.context, (WithdrawalRequest));
        _withdraw(body, true, true);
    }
}
```
