### Title
Cross-chain cancellation trusts an empty GET-response storage value as proof of "unfilled", without verifying the queried height reflects the current fill state - `ExtrinsicIntents.sol::onGetResponse`

### Summary
`ExtrinsicIntents.onGetResponse` decides whether to refund an escrowed order purely on whether the proven `_filled[commitment]` storage value is empty:

```solidity
function onGetResponse(IncomingGetResponse calldata incoming) external override onlyHost {
    _checkRelayer(incoming.relayer);
    if (incoming.response.values[0].value.length != 0) revert Filled();
    WithdrawalRequest memory body = abi.decode(incoming.response.request.context, (WithdrawalRequest));
    _withdraw(body, true, true);
}
``` [1](#0-0) 

This mirrors the Flask-HTTPAuth bug class: an "absence"/"empty" signal from a lookup is treated as conclusive proof of a negative fact ("not filled"), without constraining *which* state snapshot that emptiness was measured against. In Flask-HTTPAuth, an empty token matched empty DB rows because the verification callback ran unconditionally on missing input. Here, an empty storage slot at an attacker-chosen height is accepted as conclusive proof that an order was never filled, because the height used for the GET query is caller-supplied and only weakly constrained.

### Finding Description
`_cancelFromSource` lets the order creator dispatch a GET request for the destination-chain `_filled[commitment]` slot at an arbitrary `options.height`, with the only constraint being:

```solidity
if (options.height <= order.deadline) revert NotExpired();
``` [2](#0-1) 

This only forces the height to be *after* the deadline — it does not force the height to be the *latest* known state, nor does it require that no fill could still be pending at that height. Any state-machine height greater than the deadline for which Hyperbridge has already committed a state root (`host.stateMachineCommitment`) is accepted by `HandlerV2.handleGetResponses`, which only checks proof freshness relative to `challengePeriod`, not recency relative to `block.number`:

```solidity
uint256 delay = timestamp - host.stateMachineCommitmentUpdateTime(message.proof.height);
if (challengePeriod != 0 && challengePeriod > delay) revert ChallengePeriodNotElapsed();
...
bool valid = MerkleMountainRange.VerifyProof(root, message.proof.multiproof, leaves, message.proof.leafCount);
``` [3](#0-2) 

`onGetResponse` then treats an empty proven value at that height as proof the order was never filled, and immediately finalizes a refund (`_withdraw(body, true, true)`), which sets `_filled[commitment]` and releases the escrowed tokens back to the user:

```solidity
function _withdraw(WithdrawalRequest memory body, bool isRefund, bool finalize) internal {
    address beneficiary = address(uint160(uint256(body.beneficiary)));
    if (finalize) _filled[body.commitment] = beneficiary;
    ...
}
``` [4](#0-3) 

Because the queried height is chosen by the user at dispatch time (which can be immediately after `order.deadline`, well before a solver's later fill transaction on the destination chain is included and before Hyperbridge advances/commits a later height), the emptiness of the value at that early height does not prove the order is *currently* unfilled on the destination chain — only that it *wasn't yet* filled *at that specific historical height*. There is no check in `onGetResponse`/`_cancelFromSource` that the queried height is the destination chain's current/latest committed height, nor any reconciliation against a solver's `_fillCrossChain` that may complete at a later height still within a legitimate fill window. This is analogous to Flask-HTTPAuth trusting a lookup of an empty value as an authoritative negative, when the surrounding protocol never established that "empty" means "globally and finally absent" rather than merely "absent as of this queried snapshot."

### Impact Explanation
If a solver fills the order on the destination chain (`_fillCrossChain`, escrowing the solver's payment and dispatching `RedeemEscrow` back to source) at a height after the attacker's chosen (already-committed) query height, the order creator can concurrently drive `_cancelFromSource` → `onGetResponse` using the stale, pre-fill height to obtain a refund of the same escrowed input tokens on the source chain. Combined with the solver's independent `RedeemEscrow` claim once their fill message lands, this can result in the escrowed input tokens being paid out twice — once to the solver via `RedeemEscrow` and once to the user via the GET-response refund — causing direct loss of protocol/escrowed funds. This is unbacked/double disbursement of escrowed funds, reachable by any order creator (an unprivileged user) simply by choosing an early proof height for their permissionless cancellation GET request.

### Likelihood Explanation
Medium-to-High. The order creator fully controls `options.height` and only needs it to satisfy `height > order.deadline`; Hyperbridge commits many intermediate heights that satisfy this while still preceding a legitimate fill's inclusion height, especially in the narrow window around the deadline where solvers race to fill before expiry. No special privileges, collusion, or off-chain infrastructure control is required — a single relayed GET-response message with a permissionless proof at an unfavorable height triggers the vulnerable branch.

### Recommendation
`_cancelFromSource`/`onGetResponse` should not accept an arbitrary caller-chosen height as proof of "never filled." Either:
- Require the GET-response height to correspond to the destination chain's *latest* committed state at the time of dispatch (or enforce a minimum bound tied to when a `RedeemEscrow` for the same commitment could plausibly have landed), or
- Have `onAccept`'s `RedeemEscrow` path and `onGetResponse`'s refund path share a single source of truth check (e.g., re-verify no `RedeemEscrow` message is in flight / already delivered for this commitment) before finalizing the refund, or
- Track filled-state with a monotonically-increasing sequence/height marker so a refund at an old height cannot override a fill that is on its way based on a later height.

### Proof of Concept
1. User places a cross-chain order with `deadline = D` on chain A escrowing tokens.
2. Near `D`, a solver fills the order on chain B via `_fillCrossChain`, which sets `_filled[commitment] = solver` at destination height `H_fill` and dispatches `RedeemEscrow` back to chain A (in flight, not yet delivered).
3. Before the `RedeemEscrow` message is delivered/finalized on chain A, the user calls `_cancelFromSource` on chain A, choosing `options.height = H_query` where `D < H_query < H_fill` and Hyperbridge already has a committed state root for `H_query` (already finalized before the fill).
4. The relayer submits the GET response with a valid state proof showing `_filled[commitment]` empty at `H_query` (true, since the fill happened later at `H_fill`).
5. `onGetResponse` passes the `values[0].value.length == 0` check, calls `_withdraw(..., isRefund=true, finalize=true)`, refunding the escrow to the user.
6. Later, the `RedeemEscrow` message from step 2 lands and pays the solver from the same escrow accounting, resulting in double payout / loss of escrowed funds.

### Citations

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L240-275)
```text
    function _cancelFromSource(Order calldata order, CancelOptions calldata options, bytes32 commitment) internal {
        if (order.user != bytes32(uint256(uint160(msg.sender)))) revert Unauthorized();

        if (options.height <= order.deadline) revert NotExpired();

        uint256 inputsLen = order.inputs.length;
        for (uint256 i; i < inputsLen;) {
            if (_orders[commitment][address(uint160(uint256(order.inputs[i].token)))] == 0) revert UnknownOrder();

            unchecked {
                ++i;
            }
        }

        bytes memory context =
            abi.encode(WithdrawalRequest({commitment: commitment, tokens: order.inputs, beneficiary: order.user}));

        bytes[] memory keys = new bytes[](1);
        keys[0] = bytes.concat(abi.encodePacked(_instance(order.destination)), _calculateCommitmentSlotHash(commitment));
        DispatchGet memory request = DispatchGet({
            dest: order.destination,
            keys: keys,
            timeout: 0,
            height: options.height,
            fee: options.relayerFee,
            context: context,
            payer: msg.sender
        });

        address hostAddr = host();
        if (msg.value > 0) {
            IDispatcher(hostAddr).dispatch{value: msg.value}(request);
        } else {
            dispatchWithFeeToken(request);
        }
    }
```

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L360-366)
```text
    function onGetResponse(IncomingGetResponse calldata incoming) external override onlyHost {
        _checkRelayer(incoming.relayer);
        if (incoming.response.values[0].value.length != 0) revert Filled();

        WithdrawalRequest memory body = abi.decode(incoming.response.request.context, (WithdrawalRequest));
        _withdraw(body, true, true);
    }
```

**File:** evm/src/core/HandlerV2.sol (L217-239)
```text
    function handleGetResponses(IHost host, GetResponseMessage calldata message) external notFrozen(host) {
        uint256 timestamp = block.timestamp;
        uint256 delay = timestamp - host.stateMachineCommitmentUpdateTime(message.proof.height);
        uint256 challengePeriod = host.challengePeriod();
        if (challengePeriod != 0 && challengePeriod > delay) revert ChallengePeriodNotElapsed();

        uint256 responsesLength = message.responses.length;
        MerkleMountainRange.Leaf[] memory leaves = new MerkleMountainRange.Leaf[](responsesLength);

        for (uint256 i = 0; i < responsesLength; ++i) {
            GetResponseLeaf memory leaf = message.responses[i];
            // don't check for timeouts because it's checked on Hyperbridge

            // known request? also serves as source check
            FeeMetadata memory meta = host.requestCommitments(leaf.response.request.hash());
            if (meta.sender == address(0)) revert UnknownMessage();
            leaves[i] = MerkleMountainRange.Leaf(leaf.index, leaf.response.hash());
        }

        bytes32 root = host.stateMachineCommitment(message.proof.height).overlayRoot;
        if (root == bytes32(0)) revert StateCommitmentNotFound();
        bool valid = MerkleMountainRange.VerifyProof(root, message.proof.multiproof, leaves, message.proof.leafCount);
        if (!valid) revert InvalidProof();
```

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
