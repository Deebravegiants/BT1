### Title
Governance can front-run `placeOrder` by raising `protocolFeeBps`/`destinationProtocolFees` to silently extract more fees than the user quoted - ([File: evm/src/apps/IntentGatewayV2.sol])

### Summary
`IntentGatewayV2.placeOrder` reads `_params.protocolFeeBps` (or a `destinationHash`-keyed override) live, in the same call that escrows the user's funds, and deducts the fee before computing the order commitment. Because this parameter is mutable through cross-chain governance (`UpdateParams`, delivered via `onAccept`) with no monotonic bound and no user-supplied cap, whoever controls the governance relayer can raise the fee immediately before a pending `placeOrder` transaction lands, taking a larger cut than the user intended when they signed/broadcast the transaction, exactly mirroring the SAM `artistFee`/`affiliateFee` front-running described in the external report.

### Finding Description
`placeOrder` computes the protocol fee inline: [1](#0-0) 

```
bytes32 destinationHash = keccak256(order.destination);
uint256 protocolFeeBps = _destinationProtocolFees[destinationHash];
if (protocolFeeBps == 0) {
    protocolFeeBps = _params.protocolFeeBps;
}
...
uint256 protocolFee = (originalAmount * protocolFeeBps) / 10_000;
uint256 reducedAmount = originalAmount - protocolFee;
```

There is no upper bound check (`MAX_BPS`/`InvalidProtocolFee`-style guard) visible around this read, and the fee is applied atomically at mining time of the user's own transaction — not at the time the user built/signed/quoted the order. `_params` (including `protocolFeeBps`) and `_destinationProtocolFees` are updated by a governance-delivered `ParamsUpdate`/`UpdateParams` action processed through `onAccept`, gated only by the Hyperbridge source check and the configured relayer: [2](#0-1) 

This is structurally identical to the SAM report: a party who controls a privileged, live-adjustable fee knob (there: `artistFee`/`affiliateFee`/`affiliateMerkleRoot`; here: `protocolFeeBps`/`_destinationProtocolFees`) can watch the mempool for a user's fund-moving transaction (`buy()` there, `placeOrder` here) and, using the same block-building/Flashbots technique described in the report, change the fee to its maximum right before the user's transaction executes, then revert it afterward. The user's `msg.value`/approved amount is not itself a price-slippage bound on the *fee rate* — a user who approves 1000 USDC and expects a 5bps fee has no on-chain guarantee that the fee actually applied at inclusion time is still 5bps; it can be raised to whatever the max allowed value is (or to whatever `_params.protocolFeeBps` is set to, since no cap is visible in the excerpted code) in the same block, with the difference "retained in the gateway as dust" per the documentation: [3](#0-2) 

The SDK's own quoting flow (`quoteIntent`/`quoteOrderFees`) computes the expected reduced amount off-chain before submission and has no on-chain enforcement that the applied `protocolFeeBps` matches what was quoted — the commitment hash is only computed *after* the live fee is applied, so any value governance sets at inclusion time is what the user is charged, silently.

### Impact Explanation
An order placer submitting `placeOrder` with a specific `order.inputs` amount, expecting the currently-published `protocolFeeBps` (documented as 5bps) to apply, can have the applied fee bumped between transaction submission and inclusion by whoever controls the governance relayer key (or by an attacker who compromises/colludes with it), silently reducing the amount the user actually escrows for the solver and diverting the difference to the gateway as "dust." This is a direct value-extraction vector against unprivileged users placing intents, analogous to the artist stealing up to 15% of mint price in the referenced report, except the ceiling here depends on whatever bound (if any) exists on `protocolFeeBps` in `_validateParams`/`_setParams` (not visible in the code reviewed, so the worst case could not be bounded with certainty). Reachable from a single `placeOrder` transaction; funds are moved via the same TX that a normal user would send, with no separate confirmation step for the fee actually charged.

### Likelihood Explanation
Likelihood is bounded by the same factor the referenced report calls out: the actor must control (or be) the governance relayer/HostManager admin channel that delivers `UpdateParams`, and must race the user's `placeOrder` transaction within the same block via MEV tooling (Flashbots-style bundling: `raise-fee → user's placeOrder → restore-fee`). This is a legitimate, unprivileged-observer-exploitable MEV path once governance access is available, not a purely theoretical one — it requires no bug in proof verification or consensus, only ordinary transaction-ordering control over a governance-gated parameter that is read live inside a value-moving function.

### Recommendation
Bind the protocol fee actually charged to what the user committed to at submission time rather than reading it live from mutable governance state inside `placeOrder`. Options: (a) let the caller pass a `maxProtocolFeeBps` parameter and revert if the live `protocolFeeBps` exceeds it (mirrors slippage protection the report recommends for the analogous case); (b) apply governance fee changes only after a timelock/delay so no single block can toggle it; (c) cap `protocolFeeBps` tightly and require any change to also satisfy a maximum absolute-delta-per-update guard so an in-block, then-reverted spike cannot occur. This closely follows the report's recommendation to make the fee path revert rather than silently defaulting to a higher, unexpected fee.

### Proof of Concept
1. User calls `quoteIntent`/`quoteOrderFees`, sees `protocolFeeBps = 5` published via `params()`, and builds `placeOrder(order, graffiti)` expecting a 0.05% deduction, broadcasting the transaction.
2. The governance-relayer-controlling actor observes the pending transaction and, in the same block (via Flashbots or equivalent private bundle), submits an `onAccept` delivery carrying `ParamsUpdate{ params.protocolFeeBps = MAX }` (or a `destinationFees` override for the user's specific destination) ahead of the user's `placeOrder`, per the flow in [4](#0-3) .
3. `placeOrder` executes, reading the now-inflated `protocolFeeBps`/`_destinationProtocolFees[destinationHash]` at [5](#0-4) , deducting a much larger fee than the user expected; the difference is retained as "dust" in the gateway.
4. The actor then submits another `ParamsUpdate` restoring the original `protocolFeeBps` immediately after, in the same or next block, leaving no visible persistent state change and the user none the wiser unless they inspect the `DustCollected` event emitted at that specific block.

Note: I could not locate an explicit upper-bound check (e.g., `MAX_BPS`/`InvalidProtocolFee`) on `protocolFeeBps` within the code excerpts retrieved for `_validateParams`/`_setParams` in `IntentsBase.sol`; if such a bound exists and is small, it limits (but does not eliminate) the severity of this finding. A Devin session with full repo access should confirm the exact bound, if any, before finalizing severity.

### Citations

**File:** evm/src/apps/IntentGatewayV2.sol (L331-361)
```text
        // Phase 2: Compute protocol fees and commitment from actual received amounts.
        bytes32 destinationHash = keccak256(order.destination);
        uint256 protocolFeeBps = _destinationProtocolFees[destinationHash];
        if (protocolFeeBps == 0) {
            protocolFeeBps = _params.protocolFeeBps;
        }
        TokenInfo[] memory reducedInputs;
        bytes32 commitment;

        if (protocolFeeBps > 0) {
            reducedInputs = new TokenInfo[](inputsLen);
            for (uint256 i; i < inputsLen;) {
                uint256 originalAmount = order.inputs[i].amount;
                if (originalAmount == 0) revert InvalidInput();
                uint256 protocolFee = (originalAmount * protocolFeeBps) / 10_000;
                uint256 reducedAmount = originalAmount - protocolFee;
                address token = address(uint160(uint256(order.inputs[i].token)));

                if (protocolFee > 0) emit DustCollected(token, protocolFee);

                reducedInputs[i] = TokenInfo({token: order.inputs[i].token, amount: reducedAmount});
                unchecked {
                    ++i;
                }
            }

            order.inputs = reducedInputs;
        } else {
            reducedInputs = order.inputs;
        }
        commitment = keccak256(abi.encode(order));
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L637-660)
```text
        // only hyperbridge is permitted to perfom these actions
        if (keccak256(incoming.request.source) != keccak256(IDispatcher(host()).hyperbridge())) revert Unauthorized();
        if (kind == RequestKind.NewDeployment) {
            NewDeployment memory body = abi.decode(incoming.request.body[1:], (NewDeployment));
            _instances[keccak256(body.stateMachineId)] = body.gateway;

            emit NewDeploymentAdded({stateMachineId: body.stateMachineId, gateway: body.gateway});
        } else if (kind == RequestKind.UpdateParams) {
            // Decode the body which includes optional destination-specific protocol fee updates
            ParamsUpdate memory update = abi.decode(incoming.request.body[1:], (ParamsUpdate));
            emit ParamsUpdated({previous: _params, current: update.params});
            _params = update.params;

            // Update destination-specific protocol fees if provided
            for (uint256 i; i < update.destinationFees.length;) {
                bytes32 stateMachineId = update.destinationFees[i].stateMachineId;
                uint256 feeBps = update.destinationFees[i].destinationFeeBps;
                _destinationProtocolFees[stateMachineId] = feeBps;

                unchecked {
                    ++i;
                }
                emit DestinationProtocolFeeUpdated(stateMachineId, feeBps);
            }
```

**File:** docs/content/developers/evm/intent-gateway/placing-orders.mdx (L94-111)
```text
### Protocol fees

Before escrowing, the contract deducts a protocol fee from each input amount:

```
protocolFee = input.amount × protocolFeeBps / 10_000
reducedAmount = input.amount − protocolFee
```

The fee is retained in the gateway as dust (emitting `DustCollected`), and per-destination overrides take precedence over the global `protocolFeeBps` when set. Current deployments charge **5 bps (0.05%)**. For a 100 USDC input:

| Item | Amount |
| --- | ---: |
| USDC transferred from your wallet | 100.000000 USDC |
| Protocol fee: `100 × 5 / 10,000` | 0.050000 USDC |
| Amount actually escrowed and offered to solvers | 99.950000 USDC |

The commitment hash is computed over the **fee-reduced inputs** — solvers read the reduced amounts from the `OrderPlaced` event and only need to match those. The fee is deducted at placement and is **not refunded** if the order expires, receives no bids, or is cancelled; a cancellation returns the remaining escrow and `order.fees`, but not the protocol fee.
```
