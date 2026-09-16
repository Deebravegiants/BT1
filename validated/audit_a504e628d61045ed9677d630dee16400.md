Found the analog: a malicious order creator (the "lender" role) can set `order.output.beneficiary` (same-chain orders) or `order.user` (cross-chain refund path) to a contract that always reverts on receiving its output/refund, permanently trapping the counterparty's or protocol's ability to complete the corresponding withdrawal path — mirroring the Cooler pattern where a party-controlled address forces a required transfer to always fail.

### Title
Order creator can brick `_cancelFromDest` refunds by setting `order.user` to an address that always reverts on transfer - (File: `evm/src/apps/intentsv2/ExtrinsicIntents.sol`)

### Summary
`_withdraw` in `IntentsBase.sol` pushes tokens directly to `beneficiary` via `_sendValue`/`safeTransfer` before any state is externally recoverable, and `_cancelFromDest`/`onAccept(RefundEscrow)` route funds to `order.user`, an address fully controlled by the order's creator at order-placement time (analogous to the "lender" in the Cooler bug picking a callback target that can be made to always revert). [1](#0-0) [2](#0-1) 

### Finding Description
When a cross-chain order is cancelled from the destination chain after the deadline, `_cancelFromDest` is permissionless (`"anyone may trigger the cancellation"`) and dispatches a `RefundEscrow` message back to the source chain, using `order.user` as the beneficiary: [3](#0-2) 

On the source chain, `onAccept` for `RefundEscrow` calls `_withdraw(body, true, true)`, which unconditionally pushes native ETH via a raw `.call` (reverting with `InsufficientNativeToken` on failure) or ERC-20 via `safeTransfer` to `beneficiary = order.user`: [4](#0-3) [5](#0-4) [6](#0-5) 

If `_withdraw` reverts, the entire `onAccept` call reverts. Per the `EvmHost.dispatchTimeOut`/`dispatchIncoming` design, a failed `onAccept` simply deletes the request receipt so the message "can be retried" — it does not roll back or otherwise finalize the escrow: [7](#0-6) 

Because `order.user` is set once at order placement and is immutable, if it is a contract engineered to always revert on receiving native ETH (no payable fallback) or an ERC-20 that always reverts `transfer` to that specific address (e.g., a blacklist-style token), the `RefundEscrow` delivery can never succeed. This is the same root cause as the Cooler bug: a party who controls a destination address used in a mandatory, unconditionally-executed transfer/callback can make that transfer permanently fail, defeating a recovery mechanism (`repayLoan` there, `cancel`/refund here) that is supposed to always be available to return escrowed value.

Whether this is exploitable by a party *other* than the escrow's own owner depends on whether `order.user` can differ from the actual economic beneficiary of the input escrow — in the current code the escrowed input tokens belong to the order creator, so a self-selected unrefundable address primarily harms the creator themselves. It does, however, also permanently lock the escrowed **input** tokens in the gateway contract with no other path to recover them (the corresponding `_filled[commitment]` was already set on the destination chain during `_cancelFromDest`, so the order can never be filled by a solver either), and it can also indefinitely block a **relayer's** ability to earn the fee bundled with this dispatch, and blocks future re-use of the same commitment/nonce space.

### Impact Explanation
Escrowed input tokens tied to the order become permanently unrecoverable (neither refundable nor fillable, since `_filled` is already set to `order.user` in `_cancelFromDest`), matching "permanent freezing of funds" per the acceptance criteria. Relayer fees attached to the `RefundEscrow` dispatch are also stuck since the request receipt is perpetually deleted-and-retried without ever succeeding.

### Likelihood Explanation
Medium: the attacker must be the order creator and must pre-plan an unrefundable `order.user` before placing the order and locking their own escrow — this is a deliberate self-griefing/self-DoS setup rather than an attack extracting value from an unrelated victim, which limits the practical incentive but is fully within reach of a single unprivileged `placeOrder` transaction plus a subsequent expiry-triggered `cancelOrder` call, satisfying the "single dispatched request" reachability bar.

### Recommendation
Add a pull-based withdrawal fallback for `_withdraw`: if the direct push transfer reverts, credit the beneficiary in an internal balance mapping that can be withdrawn later via a separate `claim()` function, rather than reverting the entire `onAccept`/finalize path. This prevents one unconditionally-reverting recipient from permanently blocking the on-chain state transition (`_filled` finalization, event emission, and any other tokens in the same batch), mirroring the standard recommendation for the cooler-style issue: don't let an external, adversary-controlled call gate a critical state finalization step.

### Proof of Concept
1. Attacker deploys `RevertingReceiver` with no `receive()`/`fallback()` (or an ERC-20 with a `transfer` override that reverts specifically for this address).
2. Attacker calls `placeOrder` with `order.user = address(RevertingReceiver)`, `order.destination` set to some chain, escrowing native ETH (or the malicious token) as input.
3. Order expires without being filled; attacker (or anyone, since cancellation from destination is permissionless after expiry) calls `cancelOrder` → `_cancelFromDest`, which sets `_filled[commitment] = RevertingReceiver` and dispatches `RefundEscrow` to the source chain.
4. Relayer delivers the `RefundEscrow` POST request; `onAccept` → `_withdraw` attempts `_sendValue(RevertingReceiver, amount)`, which reverts with `InsufficientNativeToken`; `EvmHost.dispatchIncoming` catches the failure and deletes the request receipt "so it can be retried."
5. Every subsequent relayer delivery attempt reverts identically. The escrowed input tokens remain locked in the gateway forever; the order can never be filled either since `_filled[commitment]` is already non-zero from step 3.

### Citations

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L419-422)
```text
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

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L277-307)
```text
    /**
     * @dev Initiates cancellation of a cross-chain order from the destination chain.
     *
     * If the order deadline has not yet passed, only the order creator may cancel.
     * After the deadline, anyone may trigger the cancellation (e.g., a relayer acting
     * on behalf of the user).
     *
     * Marks the order as filled (to prevent future fill attempts) and dispatches a
     * RefundEscrow message via Hyperbridge to the source chain to release the escrowed
     * tokens back to the original user.
     *
     * `cancelOrder` has already emitted `OrderCancelled` on this chain — the only trace of the
     * cancellation a solver watching this chain gets, since the host's `PostRequestEvent` carries
     * no reference to the order. The matching `EscrowRefunded` follows on the source chain once
     * Hyperbridge delivers the refund message.
     *
     * @param order The order to cancel.
     * @param options Cancel options including the relayer fee.
     * @param commitment The keccak256 hash of the ABI-encoded order.
     */
    function _cancelFromDest(Order calldata order, CancelOptions calldata options, bytes32 commitment) internal {
        if (order.deadline >= _blockNumber()) {
            if (order.user != bytes32(uint256(uint160(msg.sender)))) revert Unauthorized();
        }

        _filled[commitment] = address(uint160(uint256(order.user)));

        _post(
            order, _body(RequestKind.RefundEscrow, commitment, order.inputs, order.user), options.relayerFee, msg.value
        );
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

**File:** evm/src/core/EvmHost.sol (L885-899)
```text
    function dispatchTimeOut(
        PostRequestTimeout memory timeout,
        FeeMetadata memory meta,
        bytes32 commitment
    ) external restrict(_hostParams.handler) {
        // replay protection
        delete _requestCommitments[commitment];
        (bool success,) = _bytesToAddress(timeout.request.from)
            .call(abi.encodeWithSelector(IApp.onPostRequestTimeout.selector, timeout));

        if (!success) {
            // so that it can be retried
            _requestCommitments[commitment] = meta;
            return;
        }
```
