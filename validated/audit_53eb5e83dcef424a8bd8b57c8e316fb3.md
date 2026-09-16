### Title
Protocol fee rate can change between quote and execution, causing user's escrowed order to be reduced by more than expected - ([File: evm/src/apps/IntentGatewayV2.sol])

### Summary
`IntentGatewayV2.placeOrder` deducts a `protocolFeeBps` (read live from mutable storage) from the user's input amounts at the moment the transaction executes, not at the moment the user (or their frontend) computed a quote. Because this rate is governance-updatable at any time via an inbound ISMP message, a rate change landing between quote-time and mining-time causes the user's actual escrowed/order amount (and thus what they effectively pay in protocol fee) to differ from — and be worse than — what was quoted. This is the same bug class as the Union Finance finding: a fee parameter read from live mutable state at execution time, rather than being pinned by the caller, can make the user's realized cost larger than expected, with no user-supplied cap to bound the deviation.

### Finding Description
In `placeOrder`, the protocol fee percentage applied to each input is fetched from storage at call time: [1](#0-0) 

```solidity
uint256 protocolFeeBps = _destinationProtocolFees[destinationHash];
if (protocolFeeBps == 0) {
    protocolFeeBps = _params.protocolFeeBps;
}
...
uint256 protocolFee = (originalAmount * protocolFeeBps) / 10_000;
uint256 reducedAmount = originalAmount - protocolFee;
```

`protocolFeeBps` (global) and `_destinationProtocolFees` (per-destination overrides) are mutable state set by `_updateParams`, which is invoked from an inbound Hyperbridge governance message and takes effect immediately, with no delay or timelock: [2](#0-1) 

The user computes an expected reduced/escrowed amount off-chain via `quoteIntent()`/SDK helpers before submitting `placeOrder` (documented behavior: "Do not build an order by reducing the input yourself... use `quoteIntent()`"), but there is no on-chain mechanism (e.g., a caller-supplied `maxProtocolFeeBps` or a minimum-reduced-amount bound in the `Order` struct) to guarantee the fee rate actually applied matches what was quoted. If `protocolFeeBps` (or the relevant destination override) increases between the time the user/frontend fetches the current rate and the time `placeOrder` is mined, the user's inputs are reduced by more than expected — directly analogous to `UToken.borrow` charging `amount + fee` where `fee` is read from a mutable `originationFee` at execution time rather than being bounded by a caller-specified maximum.

The protocol fee is explicitly *not refundable*: it is retained as dust immediately at placement and is not returned on expiry or cancellation, so the user cannot recover the unexpected excess fee even if the order later fails to fill: [3](#0-2) 

### Impact Explanation
An unprivileged user submitting an ordinary `placeOrder` transaction can have more of their input tokens taken as protocol fee than they expected/approved for, with the excess permanently retained by the protocol as dust (not refundable on cancel/expiry). Depending on how large a fee-rate change governance pushes through (and there is no on-chain cap validated against the user's expectation — only a global sanity check that `protocolFeeBps < 10_000` at parameter-update time), the user's realized loss can exceed what was quoted. This is a fund-loss-to-user issue reachable from a single unprivileged `placeOrder` call, matching the required "concrete theft... of funds" criterion, since the delta is retained by the protocol.

### Likelihood Explanation
The likelihood depends on how frequently `protocolFeeBps` / `_destinationProtocolFees` are updated relative to order placement latency (mempool delay, block time). Since fee updates take effect immediately upon delivery of the governance message (no timelock/grace window observed in `_updateParams`), any legitimate fee-rate change concurrent with in-flight `placeOrder` transactions will silently overcharge those orders. This does not require a malicious governance actor — a routine, benign fee adjustment is sufficient to trigger the mismatch, which is why this is flagged as a design gap rather than a malicious-governance scenario.

### Recommendation
Add a caller-specified bound to `Order` (e.g., `maxProtocolFeeBps` or `minReducedAmount` per input) and have `placeOrder` revert if the live `protocolFeeBps`/`_destinationProtocolFees` value would cause a deduction exceeding that bound. This mirrors the Union Finance recommendation of adding a `maxdebt` parameter so callers can enforce that no state change occurring between quoting and execution can cost them more than they explicitly agreed to.

### Proof of Concept
1. Off-chain: user calls `quoteIntent()` and observes current `protocolFeeBps = X` (e.g., 5 bps), computing `reducedAmount = amountIn - amountIn*X/10_000`.
2. Governance dispatches a `ParamsUpdate` (or `DestinationFee`) message increasing `protocolFeeBps` to `Y > X` (or setting a destination override), which lands and is applied via `_updateParams` before the user's `placeOrder` transaction is mined: [2](#0-1) 
3. User's previously-submitted `placeOrder` transaction is mined, and the fee is computed at the new, higher rate `Y`: [4](#0-3) 
4. The escrowed `reducedInputs` amount is lower than the user expected from their `quoteIntent()` call; the extra deducted amount is emitted as `DustCollected` and retained by the protocol permanently — not refundable even if the order is later cancelled or expires.

**Note on uncertainty:** I was unable to fully trace the exact `onAccept`/`RequestKind.UpdateParams` dispatch path within `evm/src/apps/intentsv2/ExtrinsicIntents.sol` in the final iteration (grep confirmed matches exist there but content wasn't read), so I cannot cite the precise governance-message-to-`_updateParams` call site line numbers in that file; this does not affect the core finding, which is fully supported by `IntentGatewayV2.sol` and `IntentsBase.sol`.

### Citations

**File:** evm/src/apps/IntentGatewayV2.sol (L331-349)
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
```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L611-628)
```text
    function _updateParams(ParamsUpdate memory update) internal {
        _validateParams(update.params);

        emit ParamsUpdated({previous: _params, current: update.params});
        _params = update.params;

        for (uint256 i; i < update.destinationFees.length;) {
            bytes memory chain = update.destinationFees[i].chain;
            uint256 feeBps = update.destinationFees[i].destinationFeeBps;
            if (feeBps >= 10_000) revert InvalidInput();
            _destinationProtocolFees[keccak256(chain)] = feeBps;

            unchecked {
                ++i;
            }
            emit DestinationProtocolFeeUpdated(string(chain), feeBps);
        }
    }
```

**File:** docs/content/developers/evm/intent-gateway/placing-orders.mdx (L103-115)
```text
The fee is retained in the gateway as dust (emitting `DustCollected`), and per-destination overrides take precedence over the global `protocolFeeBps` when set. Current deployments charge **5 bps (0.05%)**. For a 100 USDC input:

| Item | Amount |
| --- | ---: |
| USDC transferred from your wallet | 100.000000 USDC |
| Protocol fee: `100 × 5 / 10,000` | 0.050000 USDC |
| Amount actually escrowed and offered to solvers | 99.950000 USDC |

The commitment hash is computed over the **fee-reduced inputs** — solvers read the reduced amounts from the `OrderPlaced` event and only need to match those. The fee is deducted at placement and is **not refunded** if the order expires, receives no bids, or is cancelled; a cancellation returns the remaining escrow and `order.fees`, but not the protocol fee.

<Callout type="warn">
Do not build an order by reducing the input yourself to account for the protocol fee. Send the gross input amount and use the amounts returned by `quoteIntent()`. The quote prices the fee-reduced escrow amount; reducing it again would make the order smaller than intended.
</Callout>
```
