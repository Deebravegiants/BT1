## Analysis

The Fractional Buyout bug is a specific instance of a broader class: an unprivileged actor can make a state-finalizing function's mandatory push-transfer to an attacker-influenced address permanently unpayable, and the retry path for that failure just replays the identical call forever, so the funds (and, in Buyout's case, a shared resource) get stuck with no alternative recovery route.

Hyperbridge's core dispatch path in `EvmHost.dispatchIncoming` already defends against this for the generic app callback case — on failure it deletes the receipt so a relayer can retry [1](#0-0) . But the retry only helps if a *different* outcome is possible on resubmission. In the Intents V2 escrow-settlement path, it is not: the beneficiary of the final payout is fixed by the cross-chain message and the transfer is always a push, with no pull-based fallback.

`IntentsBase._withdraw` (used by same-chain fills/cancels and by `onAccept`/`onGetResponse` handling `RedeemEscrow`/`RefundEscrow`) unconditionally pushes tokens to a beneficiary embedded in the withdrawal request — native ETH via `_sendValue` (a raw `.call` that reverts on failure) or ERC20 via `safeTransfer`: [2](#0-1) 

The same unconditional-push pattern exists in the Tron/EVM `IntentGatewayV2.withdraw`: [3](#0-2) 

The beneficiary for a cross-chain `RefundEscrow` is always `order.user` — the account that placed the order — and `_cancelFromDest`/`_cancelFromSource` finalize (`_filled[commitment] = ...`) *before* the refund is guaranteed to land: [4](#0-3) 

For a cross-chain fill, the beneficiary of `RedeemEscrow` is `msg.sender` — the solver's own fill address: [5](#0-4) 

If that beneficiary address cannot accept the payout (a contract wallet with no compatible `receive()`, or — for ERC-20 legs — a token that reverts on transfer to a blocklisted/frozen address such as USDC), `onAccept`'s call to `_withdraw`/`withdraw` reverts. `EvmHost.dispatchIncoming` catches this and deletes the request receipt "so it can be retried" — but retrying replays the exact same transfer to the exact same unpayable beneficiary, so it fails identically every time. There is no alternate claim function, no way to change the beneficiary, and no pull-based withdrawal escape hatch anywhere in `IntentsBase`/`IntentGatewayV2`. The escrowed input tokens for that commitment (and, for `_cancelFromDest`, the order itself, which is already marked `_filled` and can never be filled by a solver either) are permanently stuck.

### Title
Escrow settlement in IntentGatewayV2/IntentsBase can be permanently frozen by an unpayable beneficiary with no pull-based recovery - (File: evm/src/apps/intentsv2/IntentsBase.sol)

### Summary
`_withdraw` (and the Tron/EVM `IntentGatewayV2.withdraw`) always pushes the final settlement (native ETH via low-level `call`, or ERC-20 via `safeTransfer`) to a beneficiary address fixed at order-placement or fill time, with no alternative pull-based withdrawal path. When that beneficiary cannot accept the transfer, the settlement call reverts every time it is attempted or retried, permanently freezing the escrowed funds.

### Finding Description
Cross-chain settlement in the Intents V2 apps always ends in an unconditional push transfer to a hard-coded beneficiary:
- `RefundEscrow` (from `_cancelFromDest`/`_cancelFromSource`) always pays `order.user`.
- `RedeemEscrow` (from `_fillCrossChain`) always pays `msg.sender` (the solver's fill address).

`_withdraw` performs these transfers unconditionally and reverts the whole `onAccept`/`onGetResponse` call if the transfer fails [2](#0-1) . `EvmHost.dispatchIncoming` treats any `onAccept` revert as "retryable" by deleting the request receipt [1](#0-0) , but nothing about a retry changes the beneficiary or the transfer mechanism — the same push to the same unpayable address is attempted again, and fails again, indefinitely.

`_cancelFromDest` compounds this: it marks the order settled locally (`_filled[commitment] = order.user`) before the refund is known to succeed, which also permanently blocks any solver from ever filling that order [4](#0-3) .

This is the same root cause as the referenced Fractional `Buyout.end()` bug: a lifecycle-finalizing function performs a mandatory push transfer to an address the protocol does not fully control, with no fallback claim mechanism if that transfer is refused.

### Impact Explanation
Any escrowed input tokens for an order whose refund/redeem beneficiary cannot accept the payout become permanently locked in the `IntentGatewayV2`/`IntentsBase` contract, with no recovery function anywhere in the codebase to reroute or pull the funds out. This can occur:
- Accidentally, if `order.user` or the solver's fill address is a smart-contract wallet without a compatible `receive()`/fallback, or if an ERC-20 leg uses a token (e.g., USDC-style) that can later blocklist the beneficiary address between order placement and settlement.
- As griefing: a solver could deliberately fill an order using a fill address that reverts on receiving native ETH, permanently freezing their own redemption — low-impact self-harm — but a user could equally place an order from a beneficiary address they later lose control of or that becomes non-payable, freezing funds the protocol has no way to recover.

This matches the "permanent freezing of funds" acceptance criterion: escrowed value becomes irrecoverable through any code path.

### Likelihood Explanation
Reachable by any unprivileged user or solver interacting with the Intent Gateway through a single order placement/fill/cancel — no privileged role or governance action is required. The failure mode is deterministic and reproducible on every retry, since the retry logic in `EvmHost.dispatchIncoming` does not alter the beneficiary or the transfer path.

### Recommendation
Add an escrow-accounting fallback for the case where the push transfer to a beneficiary fails: catch the low-level call/`safeTransfer` failure inside `_withdraw`, credit the amount to an internal per-beneficiary claimable balance instead of reverting the whole settlement, and expose a separate `claim()`/`withdraw()` function that lets the beneficiary (or, for stuck ERC-20 legs, a governance-controlled sweep) redirect or pull the funds to a different address later.

### Proof of Concept
1. User places a cross-chain order on the source chain via `IntentGatewayV2.placeOrder`, with `order.user` set to a contract address that has no payable `receive()`/`fallback()` (or, for an ERC-20 input, an address later blocklisted by the token issuer).
2. User calls `cancelOrder` from the destination chain before a solver fills it; `_cancelFromDest` marks `_filled[commitment] = order.user` and dispatches `RefundEscrow` back to the source chain [4](#0-3) .
3. A relayer delivers the `RefundEscrow` message; `onAccept` calls `_withdraw(body, true, true)`, which attempts `_sendValue(beneficiary, amount)` or `IERC20(token).safeTransfer(beneficiary, amount)` to `order.user` and reverts [2](#0-1) .
4. `EvmHost.dispatchIncoming` catches the revert and deletes `_requestReceipts[commitment]` "so it can be retried" [1](#0-0) .
5. Every subsequent relayer retry replays the identical failing transfer to the same unpayable `order.user`. The order is already `_filled` (so no solver can ever fill it instead), and the escrowed input tokens remain locked in the gateway contract permanently, with no other function available to reclaim them.

### Citations

**File:** evm/src/core/EvmHost.sol (L805-817)
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

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L207-212)
```text
        _post(
            order,
            _body(RequestKind.RedeemEscrow, commitment, order.inputs, bytes32(uint256(uint160(msg.sender)))),
            options.relayerFee,
            nativeFee
        );
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
