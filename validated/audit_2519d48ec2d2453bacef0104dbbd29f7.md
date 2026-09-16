### Title
Solver-specified `relayerFee` for `RedeemEscrow` has no minimum bound, risking indefinite loss of a filler's escrow claim on cross-chain intent fills - (File: `evm/src/apps/intentsv2/ExtrinsicIntents.sol`)

### Summary
`_fillCrossChain` lets the filler pick an arbitrary `options.relayerFee` for the `RedeemEscrow` message that is dispatched back to the source chain to release the escrowed input tokens to them. This is directly analogous to the reported `_l2Gas` issue: a user-controlled parameter that funds the delivery of a cross-chain message, where setting it too low can strand the associated funds because no relayer is economically motivated to deliver the message.

### Finding Description
After a solver fills a cross-chain order, `_filled[commitment]` is set to the solver and a `RedeemEscrow` post request is dispatched via `_post`, carrying `options.relayerFee` chosen by the caller: [1](#0-0) 

`_post` builds the `DispatchPost` with `timeout: 0` (i.e., the request never times out) and the caller-supplied `relayerFee`: [2](#0-1) 

Because the fee is not validated against any protocol-defined minimum (e.g., an on-chain estimate of the destination `handlePostRequests` + consensus-verification cost, as `EvmChain.estimateGas` computes off-chain), a solver who under-prices `relayerFee` produces a message that sits on Hyperbridge indefinitely — no relayer has incentive to submit the proof and pay `handlePostRequests` gas for less than it costs them. This is the same root cause as the reported `L1ECOBridge` issue: the fee/gas parameter that funds destination execution is user-chosen and unchecked at the contract level, and an inadequate value stalls delivery of the message that is the *only* path to recovering the associated funds.

Once `_filled[commitment] = msg.sender` is set, both cancellation paths (`_cancelFromSource`, `_cancelFromDest`) are permanently foreclosed for this order — they only operate on unfilled orders, and cross-chain fills are all-or-nothing. Thus the escrowed input tokens on the source chain can only ever be released via successful delivery of the `RedeemEscrow` message; there is no timeout-triggered refund path (the request's `timeout` field is `0`), and no alternate route to "re-price" the stuck relayer fee once dispatched — the payer (solver) would have to independently self-relay by paying the destination gas directly (the protocol's fee is separate from any built-in requirement that gas price cover proof-verification cost).

### Impact Explanation
If `options.relayerFee` is set below the actual cost of delivering `RedeemEscrow` (proof verification + `onAccept`/`withdraw` execution on the source chain), no rational relayer will submit it. The escrowed input tokens that the solver is entitled to receive become effectively frozen — reachable only by the filler manually constructing and submitting the proof/delivery transaction themselves at a loss (paying delivery gas without the fee compensating for it), which is not guaranteed to be economical or even accessible to average users/solvers. This is a fund-freezing bug reachable from a single `fillOrder` transaction on the destination chain.

### Likelihood Explanation
Likelihood is Medium: the SDK's `estimateFillOrder`/`quoteOrderFees` normally computes a conservative `RELAYER_MESSAGE_GAS` (1,000,000 gas) budget with headroom before calling `fillOrder`, so well-behaved SDK-driven fills are unlikely to under-price the fee: [3](#0-2) 
However, `fillOrder`/`_fillCrossChain` itself performs no on-chain validation of `options.relayerFee`, so any solver bypassing the SDK's estimator (custom integration, a bug in a bot's fee logic, or a deliberately cheap fill during gas-price spikes) can dispatch an under-funded `RedeemEscrow` message, at which point the loss is borne by that solver with no recovery mechanism in the contract itself.

### Recommendation
Enforce a protocol-level minimum `relayerFee` for `RedeemEscrow`/`RefundEscrow` dispatches in `_fillCrossChain`/`_cancelFromDest` (e.g., derived from a stored or governance-configured gas-price/gas-unit floor per destination-state-machine, similar to how `EvmHost`/`IHost` fee accounting already tracks per-request fee metadata), reverting `fillOrder` if the supplied fee is insufficient, rather than allowing an arbitrarily low value to be dispatched and left permanently unrelayed.

### Proof of Concept
1. A solver calls `fillOrder(order, options)` for a cross-chain order with `options.relayerFee` set to `1` wei (or `0`), and delivers the required output tokens to the beneficiary.
2. `_fillCrossChain` marks `_filled[commitment] = solver` and dispatches the `RedeemEscrow` post request with `timeout: 0` and the negligible `relayerFee`: [4](#0-3) 
3. No relayer submits `handlePostRequests` for this commitment because the fee does not cover proof-verification + execution cost on the source chain.
4. The source-chain escrow (`order.inputs`) remains locked; since `_filled[commitment]` is already set, neither `_cancelFromSource` nor `_cancelFromDest` can be invoked for this order, and the request has no timeout, so there is no protocol-native path to reclaim the funds.

### Citations

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

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L164-220)
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
    }
```

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
