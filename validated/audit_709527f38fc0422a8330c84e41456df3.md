### Title
Permanent Freezing of Escrowed Funds via Zero-Address `order.user` in `_cancelFromDest` - ([File: evm/src/apps/intentsv2/ExtrinsicIntents.sol])

### Summary
`_cancelFromDest` finalizes a cross-chain intent order by writing the caller-controlled `order.user` field directly into the `_filled` completion-tracking mapping, the same sentinel-zero pattern flagged in the external report (writing the zero value into a "one-time action" mapping defeats the `!= address(0)` guard). If the order placer sets `order.user = bytes32(0)`, `_filled[commitment]` is written but remains `address(0)` — the exact value that represents "not yet finalized" — so the top-level `Filled()` guard never trips, and the dispatched `RefundEscrow` message is built with `beneficiary = bytes32(0)`, which permanently and unconditionally reverts on delivery for any ERC‑20 input, freezing the escrowed tokens forever.

### Finding Description
`IntentsBase._filled` is documented as: "A non-zero value indicates the order has been finalized and cannot be filled again" [1](#0-0) . Both `fillOrder` and `cancelOrder` gate on `_filled[commitment] != address(0)` to enforce the one-time-finalization invariant (see the analogous gate in `IntentGatewayV2.fillOrder`: [2](#0-1) , and `cancelOrder`: [3](#0-2) ).

`_cancelFromDest` finalizes a cross-chain cancellation like this:

```solidity
function _cancelFromDest(Order calldata order, CancelOptions calldata options, bytes32 commitment) internal {
    if (order.deadline >= _blockNumber()) {
        if (order.user != bytes32(uint256(uint160(msg.sender)))) revert Unauthorized();
    }
    _filled[commitment] = address(uint160(uint256(order.user)));
    _post(order, _body(RequestKind.RefundEscrow, commitment, order.inputs, order.user), options.relayerFee, msg.value);
}
``` [4](#0-3) 

`order` is fully attacker-supplied at `placeOrder` time — the placer chooses the `order.user` value with no requirement that it equal `msg.sender` (only the *cancel/select* paths compare it against the caller, e.g. `_cancelFromSource`: [5](#0-4) ). This mirrors exactly the vesting bug's structure: a user-writable field is fed directly into a mapping whose zero value doubles as the "unused" sentinel, so choosing zero silently no-ops the "mark as done" write.

If `order.user == bytes32(0)`:
1. After the order's deadline passes, `cancelOrder` is permissionless (`_cancelFromDest`'s deadline check exempts anyone once expired).
2. `_filled[commitment] = address(uint160(uint256(bytes32(0)))) = address(0)` — i.e. the finalize step is a no-op; `_filled[commitment]` is indistinguishable from an order that was never touched.
3. A `RefundEscrow` message is dispatched to the source chain with `beneficiary = bytes32(0)` [6](#0-5) .
4. On the source chain, `onAccept` routes this into `_withdraw`, which derives `beneficiary = address(uint160(uint256(body.beneficiary)))` = `address(0)` and attempts `IERC20(token).safeTransfer(beneficiary, amount)` for every escrowed ERC‑20 input [7](#0-6) . OpenZeppelin's ERC-20 `_transfer` unconditionally reverts on `to == address(0)`, so this delivery **always reverts**.
5. Because the destination-side `_filled[commitment]` never actually became non-zero, `cancelOrder` can be called again and again (each time re-charging the relayer fee and re-dispatching an undeliverable message), while the source-chain escrow (`_orders[commitment][token]`) is never decremented because `_withdraw` never completes successfully for ERC-20 inputs. The order is simultaneously unfillable (expired, so `fillOrder`'s `Expired()` check blocks it) and uncancelable (every refund attempt reverts on delivery), permanently locking the escrowed input tokens in the gateway contract with no remaining code path to recover them.

### Impact Explanation
This permanently freezes the escrowed ERC‑20 input tokens for any order whose creator (or a relayer placing an order on a user's behalf) sets `order.user = bytes32(0)`, with no way to ever cancel or refund them once the deadline passes — the `RefundEscrow` message is structurally undeliverable (a "route unable to deliver messages" per the accepted impact classes), and the funds sit unclaimed in `IntentsBase._orders` forever. It also allows unbounded, permissionless re-dispatch of Hyperbridge POST requests for the same order (wasting relayer fees and generating garbage cross-chain traffic) since the `_filled` finalize step never sticks.

### Likelihood Explanation
The trigger requires only a single unprivileged `placeOrder` call with a crafted `order.user = bytes32(0)` field — no special privileges, no race condition, and no cooperation from other parties. It is reachable directly through the intent gateway's user-facing entrypoints (`placeOrder`/`cancelOrder`), the exact "intent solver"/order-placer attack surface this scan focuses on.

### Recommendation
Reject zero-value beneficiaries before they are written into `_filled` or dispatched as a `WithdrawalRequest.beneficiary`. Specifically, in `_cancelFromDest` (and defensively in `_withdraw`/`_cancelFromSource`), revert if `order.user == bytes32(0)` before setting `_filled[commitment]` and before building the `RefundEscrow` body, mirroring the vesting fix's recommendation of validating the recipient is never the zero address.

### Proof of Concept
1. Call `placeOrder` for a cross-chain order with `order.user = bytes32(0)`, `deadline = D`, and an ERC-20 input token escrowed normally.
2. Let block height pass `D` without any solver filling the order.
3. Anyone calls `cancelOrder(order, options)` on the destination chain. `_cancelFromDest` executes: `_filled[commitment] = address(0)` (a no-op write) and dispatches `RefundEscrow` with `beneficiary = bytes32(0)`.
4. When Hyperbridge delivers this to the source chain, `onAccept` → `_withdraw` calls `IERC20(token).safeTransfer(address(0), amount)`, which reverts every time — the message can never be successfully processed.
5. `cancelOrder` can be invoked again (step 3 repeats indefinitely, since `_filled[commitment]` was never actually set to non-zero), but the escrowed ERC-20 balance in `_orders[commitment][token]` is never released — the tokens are permanently stuck in the gateway contract.

I was not able to execute this against a live Foundry test harness in this session (read-only analysis), so the exact revert behavior of the ISMP host's retry/undelivered-message handling around step 4 should be confirmed with a Foundry PoC before remediation is finalized. [8](#0-7)

### Citations

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L122-126)
```text
    /**
     * @dev Maps order commitment hashes to the address that filled or refunded the order.
     * A non-zero value indicates the order has been finalized and cannot be filled again.
     */
    mapping(bytes32 => address) public _filled;
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

**File:** evm/src/apps/IntentGatewayV2.sol (L462-462)
```text
        if (_filled[commitment] != address(0)) revert Filled();
```

**File:** evm/src/apps/IntentGatewayV2.sol (L505-508)
```text
    function cancelOrder(Order calldata order, CancelOptions calldata options) public payable nonReentrant {
        bytes32 commitment = keccak256(abi.encode(order));

        if (_filled[commitment] != address(0)) revert Filled();
```

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L240-241)
```text
    function _cancelFromSource(Order calldata order, CancelOptions calldata options, bytes32 commitment) internal {
        if (order.user != bytes32(uint256(uint160(msg.sender)))) revert Unauthorized();
```

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L297-307)
```text
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
