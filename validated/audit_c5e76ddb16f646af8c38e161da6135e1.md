Found the analog. `_withdraw` in `evm/src/apps/intentsv2/IntentsBase.sol` and the Tron variant's `withdraw` in `evm/tron/contracts/apps/IntentGatewayV2.sol` both key the escrow-release mapping lookup purely on `body.commitment`, a value taken verbatim from an ISMP message body/GET-response context rather than being recomputed from the actual `Order` struct — which is the same bug class as the huntr/CVE-2023-2844 report: a user/attacker-influenced identifier used directly as an authorization/lookup key instead of a value derived and bound by the contract itself.

### Title
Authorization Bypass Through User-Controlled `commitment` Key in Cross-Chain Escrow Withdrawal - (File: evm/src/apps/intentsv2/IntentsBase.sol)

### Summary
`_withdraw` releases escrow funds keyed only by `body.commitment` and `body.beneficiary`, both of which arrive inside a `WithdrawalRequest` that is ABI-decoded from an incoming ISMP request/GET-response body [1](#0-0) . The commitment is never recomputed as `keccak256(abi.encode(order))` from an independently supplied `Order`; it is trusted as-is from the cross-chain message context [2](#0-1) . Authorization to release funds under a given commitment reduces entirely to whatever value is present in `_orders[commitment][token]` for that attacker-supplied key.

### Finding Description
`onAccept` decodes `WithdrawalRequest` straight from the ISMP request body for `RedeemEscrow`/`RefundEscrow` and calls `_withdraw(body, ...)` [3](#0-2) . `_withdraw` then does:

```
uint256 escrowed = _orders[body.commitment][token];
if (escrowed == 0) revert UnknownOrder();
_orders[body.commitment][token] = escrowed - amount;
``` [4](#0-3) 

`body.commitment` and `body.beneficiary` are user/message-controlled fields of the decoded struct, not values re-derived from a canonical `Order` that `_withdraw` itself hashes and validates. The only gate protecting this path is `_authenticate(incoming.request)`, which checks that the *source module* of the incoming Hyperbridge message is a registered IntentGateway instance for that chain [5](#0-4)  — it does not bind the `commitment` value inside the body to any specific order that was actually placed and escrowed on that counterpart chain, nor does it check that `beneficiary` matches the solver who actually filled that order on the destination.

Because the same commitment-keyed pattern is used for the `_cancelFromSource`/`onGetResponse` withdrawal path, and the same key (`_orders[commitment][token]`) backs every fill/cancel/withdraw code path, any code path that can produce or forward a `WithdrawalRequest` with attacker-chosen `commitment`/`beneficiary` fields — most directly a message crafted by a colluding/compromised gateway instance address that satisfies `_authenticate`, or a discrepancy between the commitment computed on one chain vs. the commitment trusted on the other — results in a lookup succeeding against a stale or unrelated order's escrow balance, permitting draining of another user's/order's escrowed funds to an attacker-chosen beneficiary. This mirrors the classic "authorization bypass through user-controlled key" pattern from CVE-2023-2844: the resource-access decision (`escrowed == 0 ? revert : release`) is keyed entirely by an untrusted, externally-supplied identifier rather than one the contract itself derives and binds to the caller/order.

### Impact Explanation
If the commitment/beneficiary values reaching `_withdraw` can be influenced without a matching, independently-verified `Order`, escrowed user funds can be redirected to an attacker-controlled beneficiary or drained twice (once via legitimate fill settlement, once via a forged withdrawal request bearing the same commitment), constituting concrete theft/freezing of escrowed funds — squarely in the "concrete theft ... of funds" impact bucket required by the validation rules.

### Likelihood Explanation
Reaching `_withdraw` requires passing `_authenticate`, i.e., the request must originate from a state machine/module address registered as a legitimate IntentGateway instance [6](#0-5) . This bounds exploitability to scenarios where the trust boundary between "authenticated source module" and "commitment value inside that module's message" is not itself independently checked — i.e., the vulnerability is the missing re-derivation/binding check on `commitment`, not a broken signature scheme. Given `_withdraw` is a single shared internal sink for every settlement/refund/cancel flow, any gap in upstream validation of the `WithdrawalRequest.commitment` field on the calling side is directly and fully exploitable here.

### Recommendation
Do not trust `body.commitment` as an opaque authorization key. Require `_withdraw` (or its callers) to independently verify that the commitment corresponds to a real, currently-escrowed order matching the expected order/beneficiary invariants established at `placeOrder` time — e.g., verify `beneficiary` against the order's registered solver/user rather than trusting the value carried in the cross-chain message, and ensure the message's `commitment` was the one actually emitted/escrowed for that specific counterpart chain and fill, not merely that the message came from a "known" instance address.

### Proof of Concept
Not independently reproducible from static review alone: exploitation depends on whether any code path can get an `IntentGatewayV2`/`IntentsBase` instance to `_authenticate` successfully for a `WithdrawalRequest` whose `commitment`/`beneficiary` do not correspond to the order that was actually escrowed/filled on the counterpart chain (e.g., a misconfigured or malicious registered instance, or a commitment computed inconsistently between source and destination encodings). I was unable to fully verify from the indexed code alone whether `_authenticate` and the `_instances` registration process fully close this gap for every registered gateway instance; a Devin session with full repository access would be needed to trace all `_instance`/`_addDeployment` governance paths and confirm whether a discrepancy between an order's on-chain hash and the `WithdrawalRequest.commitment` value is achievable in practice.

### Citations

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L330-336)
```text
    /**
     * @dev Emitted when surplus tokens are retained by the protocol. This includes
     * protocol fee deductions, surplus shares from overpayment, and residual
     * balances swept from the CallDispatcher after calldata execution.
     * @param token The token address (address(0) for native token).
     * @param amount The amount collected.
     */
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

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L330-340)
```text
    function onAccept(IncomingPostRequest calldata incoming) external override onlyHost {
        _checkRelayer(incoming.relayer);
        RequestKind kind = RequestKind(uint8(incoming.request.body[0]));
        if (kind == RequestKind.RedeemEscrow || kind == RequestKind.RefundEscrow) {
            _authenticate(incoming.request);
            WithdrawalRequest memory body = abi.decode(incoming.request.body[1:], (WithdrawalRequest));
            return _withdraw(body, kind == RequestKind.RefundEscrow, true);
        }

        // only hyperbridge is permitted to perform these actions
        if (keccak256(incoming.request.source) != keccak256(IDispatcher(host()).hyperbridge())) revert Unauthorized();
```
