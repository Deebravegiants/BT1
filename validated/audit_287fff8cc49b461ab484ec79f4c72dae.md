### Title
Cross-chain escrow refunds via `_sendValue` let a malicious `order.user` permanently freeze their own escrow and grief every relayer that attempts delivery - ([File: evm/src/apps/intentsv2/IntentsBase.sol])

### Summary
`IntentGatewayV2`'s cross-chain intent flow releases native-token escrow to `order.user`/beneficiary addresses using an unbounded-gas raw `call`. Because delivery of the underlying Hyperbridge message is permissionless (any relayer can submit the proof), and the host does not reward relayer fees unless the app-level handler succeeds, an order creator can set a malicious refund address whose fallback always reverts or burns gas — this both freezes the escrowed funds forever and drains gas from every relayer who attempts (and must re-attempt) delivery, exactly mirroring the ElFi `GasProcess`/fallback-griefing bug class.

### Finding Description
`_sendValue` performs a raw, unbounded-gas call and reverts the entire caller context if the recipient's call fails: [1](#0-0) 

This helper is used by `_withdraw`, the function that finalizes escrow release/refund for both same-chain and cross-chain orders, whenever the escrowed asset is native token: [2](#0-1) 

For cross-chain orders, the refund path is reached via a `RefundEscrow` message dispatched from the destination chain (or the cancellation GET-response flow) and delivered by a permissionless relayer through `EvmHost.dispatchIncoming`, which invokes the app's `onAccept`/`onGetResponse` with a low-level `.call` and only pays the relayer their fee **if that call succeeds**: [3](#0-2) 

Because `order.user` (the beneficiary of a refund) is fully attacker-controlled (any EOA/contract chosen at `placeOrder` time), a malicious user can:
1. Deploy a contract as `order.user`/beneficiary whose `receive()`/`fallback()` always reverts (or consumes all forwarded gas).
2. Place and then let the order expire, triggering the `RefundEscrow` cross-chain flow (`_cancelFromSource` → GET request → `onGetResponse` → `_withdraw`, or the equivalent for cross-chain refunds).
3. Every relayer that submits the state/consensus proof to deliver this message triggers `onAccept`/`onGetResponse` → `_withdraw` → `_sendValue`, which always reverts. `EvmHost.dispatchIncoming` catches this failure and does **not** revert the relayer's whole transaction, but it also does **not** reward the relayer's fee (the `if (success)` branch that pays `fee` is skipped), while the relayer has already spent gas verifying the state/consensus proof and attempting the call.
4. The commitment/receipt is deleted so the message remains "undelivered" and can be resubmitted indefinitely — meaning the escrowed native tokens can never be released, and any relayer (or the protocol's own relayer network) that tries to process this order's refund is repeatedly gas-griefed.

This is architecturally identical to the ElFi Protocol bug: a keeper/relayer executing a protocol-mandated refund to a user-controlled address with unbounded forwarded gas, where the address's fallback can revert or consume gas to grief the executor and permanently block the operation.

### Impact Explanation
- **Permanent freezing of funds**: the escrowed native-token input can never be refunded to the malicious `order.user`, since the "correct" beneficiary (by protocol logic) is always the reverting contract — the funds are stuck in the `IntentGatewayV2` escrow indefinitely.
- **Relayer/keeper gas griefing**: every relayer that attempts to deliver the refund message (a first-come, permissionless action incentivized by relayer fees) spends gas on proof verification and the failed call without being paid the relayer fee, since `EvmHost.dispatchIncoming`/`dispatchTimeOut`-style reward payouts are conditioned on `onAccept`/`onGetResponse` succeeding.
- This can be triggered by any unprivileged user simply by setting up their own order with a hostile beneficiary contract, requiring no special permissions — matching a Medium/High severity freezing-of-funds and relayer-DoS pattern.

### Likelihood Explanation
High likelihood: placing an order with a malicious contract as `order.user`/beneficiary and letting it expire is trivial and fully within an ordinary user's control; no privileged role or race condition is required. The only mitigating factor is that the primary victim of the frozen funds is the attacker themselves (their own escrow), but the relayer-griefing effect harms third parties (the permissionless relayer network) and can degrade the overall reliability/liveness of message delivery for that order lane.

### Recommendation
Do not use raw unbounded-gas `call` when sending native tokens to attacker-influenced addresses (`order.user`/beneficiary) in a code path invoked by a keeper/relayer. Options:
- Use a fixed, small gas stipend (e.g., `transfer`-equivalent 2300 gas or an explicit gas cap) for the refund call, and fall back to a pull-based withdrawal pattern (credit an internal balance the user can later withdraw themselves) if the push transfer fails, instead of reverting the whole finalize step.
- Ensure relayer fee rewards are still paid even when the refund push fails, so relayers are not penalized for a condition entirely caused by the payee.

### Proof of Concept
1. Attacker deploys `MaliciousBeneficiary` with a `receive()` that runs `while(true){}` or simply `revert()`.
2. Attacker calls `placeOrder` cross-chain with `order.user` = `MaliciousBeneficiary`, input = native ETH, and lets the order expire without being filled.
3. Attacker (or anyone) initiates `_cancelFromSource`, dispatching the GET/refund flow through Hyperbridge.
4. A relayer submits the proof to deliver the refund message; `ExtrinsicIntents.onAccept`/`onGetResponse` calls `_withdraw` → `_sendValue(MaliciousBeneficiary, amount)`, which reverts because the fallback burns gas/reverts.
5. `EvmHost.dispatchIncoming` swallows the failure, deletes the receipt, and does not pay the relayer's fee — the message remains "pending" forever, the escrow is permanently frozen, and every future relayer who tries to deliver it repeats the wasted-gas failure.

Note: I was not able to fully trace the exact `RequestKind.RefundEscrow` dispatch/switch statement inside `ExtrinsicIntents.onAccept` within the available iterations (the file read was cut off before reaching that switch); confirming the precise call site for `_withdraw` in the `RefundEscrow`/`RedeemEscrow` handling should be verified by reading the remainder of `evm/src/apps/intentsv2/ExtrinsicIntents.sol` (particularly the `onAccept` and `onGetResponse` bodies) in a follow-up session.

### Citations

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L418-422)
```text
    /// @dev Native transfer that reverts with `InsufficientNativeToken` if refused.
    function _sendValue(address to, uint256 amount) internal {
        (bool sent,) = to.call{value: amount}("");
        if (!sent) revert InsufficientNativeToken();
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

**File:** evm/src/core/EvmHost.sol (L824-847)
```text
    function dispatchIncoming(GetResponse memory response, address relayer) external restrict(_hostParams.handler) {
        // replay protection
        bytes32 commitment = response.request.hash();
        _responseReceipts[commitment] = ResponseReceipt({
            relayer: relayer,
            responseCommitment: response.hash()
        });

        (bool success,) = _bytesToAddress(response.request.from)
            .call(abi.encodeWithSelector(IApp.onGetResponse.selector, IncomingGetResponse(response, relayer)));

        if (!success) {
            // so that it can be retried
            delete _responseReceipts[commitment];
            return;
        }

        // reward the relayer fee
        uint256 fee = _requestCommitments[commitment].fee;
        if (fee != 0) {
            IERC20(feeToken()).safeTransfer(relayer, fee);
        }
        emit GetRequestHandled({commitment: commitment, relayer: relayer});
    }
```
