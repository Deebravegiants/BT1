## Analysis

The reported bug class — a "push" pattern where any single recipient of an escrow payout can revert to block settlement — has a direct analog in Hyperbridge's Intent Gateway cross-chain settlement path.

### Title
Malicious solver can permanently freeze a user's cross-chain escrowed order via a reverting beneficiary in `_withdraw` - (File: `evm/src/apps/intentsv2/IntentsBase.sol`)

### Summary
`ExtrinsicIntents._fillCrossChain` lets any solver fill a cross-chain order and dispatches a `RedeemEscrow` message whose beneficiary is hard-coded to `msg.sender` (the filler itself). When that message is delivered on the source chain, `onAccept` calls `_withdraw`, which pushes the escrowed input tokens directly to that beneficiary with no fallback if the transfer reverts.

### Finding Description
`_fillCrossChain` sets the filler as the sole beneficiary of the redemption message: [1](#0-0) 

On the source chain, `onAccept` decodes the immutable `WithdrawalRequest` and calls `_withdraw`, which "pushes" every escrowed token straight to `beneficiary`: [2](#0-1) 

using `_sendValue`, which reverts the whole call if the recipient's `call{value:}` fails: [3](#0-2) 

Since `beneficiary` is fixed at dispatch time (it is part of the ISMP `PostRequest` body and cannot be changed), if a malicious solver fills the order using a contract address that unconditionally reverts on receiving native token (or an ERC777/hook token that reverts), `_withdraw` — and therefore `onAccept` — will always revert for that specific message.

`EvmHost.dispatchIncoming` was hardened against a *different* class of DoS (one bad message bricking a whole batch): a failed `onAccept` call only deletes that message's own receipt and returns, "so that it can be retried": [4](#0-3) 

However, retrying delivers the *exact same* immutable request body with the same poisoned beneficiary, so the retry deterministically fails again. There is no mechanism (pull-payment mapping, alternate beneficiary, or timeout/refund path) to recover the escrowed input tokens once `_filled[commitment]` has already been set to the malicious solver in `_fillCrossChain`. The order is marked filled on the destination chain and the input tokens are permanently stuck in escrow on the source chain — precisely the "push over pull" failure mode described in the external report, just narrowed to a single, self-selected beneficiary instead of a multi-party split.

### Impact Explanation
A malicious actor can deliberately act as a solver, fill a legitimate cross-chain order with a contract wallet designed to reject the native-token payout (or an ERC777/callback token designed to revert on receipt), and thereby permanently lock the user's escrowed principal on the source chain with no recovery path available to the user, the solver, or ordinary relayers. This is a permanent freezing of user funds reachable from a single, unprivileged `fillOrder` call plus a single relayed ISMP delivery — no admin, governance, or privileged role is required to trigger it.

### Likelihood Explanation
Triggering this requires only: (1) deploying a trivial reverting contract, (2) calling `fillOrder` as that contract on the destination chain with sufficient output tokens to satisfy the order, and (3) waiting for/relaying the resulting `RedeemEscrow` message. No special privileges, timing races, or capital beyond the order's own output requirement are needed, making this practically reproducible by any user willing to sacrifice the output tokens they must deliver in order to freeze the corresponding (potentially much larger) escrowed input.

### Recommendation
Adopt a pull-payment pattern for `_withdraw`/`RedeemEscrow`/`RefundEscrow` settlement: on payout failure, credit the beneficiary's balance in a claimable mapping (per token) instead of reverting the whole `onAccept`, and expose a separate `claim()` function beneficiaries can call to pull their funds (with a plain ERC20/native transfer that reverts only their own claim, not the entire settlement). This preserves the observable "escrow released" state transition even when a hostile beneficiary sabotages the direct transfer, and removes the ability for a solver to weaponize `fillOrder` into a permanent freeze of user escrow.

### Proof of Concept
1. Attacker deploys `MaliciousFiller`, a contract with `receive()`/`fallback()` that always reverts (or, for ERC20 outputs paid in an ERC777-like hook token, a `tokensReceived` hook that reverts).
2. Attacker calls `fillOrder(order, options)` from `MaliciousFiller`, supplying the required output amount so `_fillCrossChain` succeeds, sets `_filled[commitment] = address(MaliciousFiller)`, and dispatches `RedeemEscrow` with `beneficiary = address(MaliciousFiller)` (`evm/src/apps/intentsv2/ExtrinsicIntents.sol:164-219`).
3. A relayer delivers the `RedeemEscrow` PostRequest; `EvmHost.dispatchIncoming` calls `onAccept` → `_withdraw`, which attempts `_sendValue(beneficiary, amount)` and reverts because `MaliciousFiller` rejects the payment (`evm/src/apps/intentsv2/IntentsBase.sol:418-470`).
4. `dispatchIncoming` deletes the receipt so the message "can be retried" (`evm/src/core/EvmHost.sol:809-816`), but every retry replays the same immutable body with the same poisoned beneficiary and fails identically — the user's original escrowed input tokens for that order remain locked in the gateway indefinitely, with `_filled[commitment]` already pointing at the attacker's address, precluding any cancellation/refund path.

### Citations

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L207-212)
```text
        _post(
            order,
            _body(RequestKind.RedeemEscrow, commitment, order.inputs, bytes32(uint256(uint160(msg.sender)))),
            options.relayerFee,
            nativeFee
        );
```

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

**File:** evm/src/core/EvmHost.sol (L805-818)
```text
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
