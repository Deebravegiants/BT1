### Title
IntentGatewayV2.placeOrder Has No Slippage/Maximum-Fee Protection Against `protocolFeeBps` Changes Front-Running Order Placement - ([File: evm/src/apps/IntentGatewayV2.sol])

### Summary
`IntentGatewayV2.placeOrder()` reads the current, mutable `protocolFeeBps` (or a destination-specific override) at execution time and uses it to compute the amount actually escrowed for the order, with no user-supplied bound on the fee that may be applied. This is the same bug class as the reported `Pool.buy` issue: a value that a pending transaction is exposed to (`weeklyPremium` there, `protocolFeeBps` here) can be changed by another transaction that lands first, causing the user to receive materially less/pay materially more than what they signed for, with no parameter to guarantee a minimum acceptable outcome or revert.

### Finding Description
`placeOrder` computes the protocol fee and the escrowed (committed) amount from state that can change between the time the user signs/submits the transaction and the time it is mined: [1](#0-0) 

```
bytes32 destinationHash = keccak256(order.destination);
uint256 protocolFeeBps = _destinationProtocolFees[destinationHash];
if (protocolFeeBps == 0) {
    protocolFeeBps = _params.protocolFeeBps;
}
...
uint256 protocolFee = (originalAmount * protocolFeeBps) / 10_000;
uint256 reducedAmount = originalAmount - protocolFee;
...
order.inputs = reducedInputs;
```

The identical pattern exists in the Tron deployment: [2](#0-1) 

The user sends a fixed gross `order.inputs[i].amount`; the contract deducts a fee at the *currently configured* rate and escrows/commits to only the `reducedAmount`. The commitment hash and the `OrderPlaced` event are computed over the reduced (post-fee) inputs, so what the solver ultimately sees and matches is whatever `protocolFeeBps`/`_destinationProtocolFees` happened to be at inclusion time — not at submission time. The docs confirm the design and current expectations: [3](#0-2) 

There is no field on `Order` or any parameter to `placeOrder` that lets the caller specify "escrow at least X" or "revert if the effective protocol fee exceeds Y bps." `protocolFeeBps` and `_destinationProtocolFees` are governance/admin-controlled parameters (set via `setParams`/destination-fee setters), and the SDK explicitly warns that the amount to escrow must be read live from `quoteIntent()` rather than computed client-side, precisely because the effective rate is only known at execution time: [4](#0-3) 

This is structurally the same defect as `Pool.buy`: the price-determining parameter (`weeklyPremium` there, `protocolFeeBps`/`_destinationProtocolFees` here) is read fresh at execution rather than pinned by the caller, and no maximum/minimum bound parameter exists to make the transaction revert if that parameter moved unfavorably between submission and inclusion.

### Impact Explanation
If a fee-parameter update transaction (e.g., raising `protocolFeeBps` or setting a higher `_destinationProtocolFees[destinationHash]`) is included ahead of — or in the same block window as — a user's `placeOrder` transaction, the user's order is escrowed and committed at a worse (higher-fee) rate than they intended when signing. Because the commitment is computed over the *reduced* inputs, the user cannot later contest the amount; the extra amount is permanently retained by the protocol as "dust" (`DustCollected`) and is not refundable even on cancellation of that reduced fee delta. This is a direct, unbacked value loss to the user for every affected order — a Medium/High severity issue depending on the magnitude of fee changes governance can push and the value of affected orders.

### Likelihood Explanation
`placeOrder` is a permissionless, frequently-invoked entry point reachable by any user placing an intent order — no privileged role is required to trigger the loss; only a routine fee-parameter update (a normal governance operation, not a malicious one) needs to be pending concurrently with user transactions, which is a realistic and recurring operational scenario (protocol fee schedules are expected to change over time, as shown by the multiple `protocolFeeBps` test configurations in the test suite). Any mempool-visible `placeOrder` call is exposed to this every time a fee parameter is adjusted.

### Recommendation
Add an explicit user-supplied bound to `placeOrder` (e.g., `minEscrowedAmount[]` per input token, or a `maxProtocolFeeBps` parameter) and revert if the fee computed at execution time would reduce any input below the caller's specified minimum / exceed the caller's specified maximum fee — mirroring the `Pool.buy` fix pattern of adding a maximum-amount parameter and reverting when the on-chain-computed value exceeds it.

### Proof of Concept
1. User calls `quoteIntent()`/observes docs stating the current fee is 5 bps and submits `placeOrder(order, graffiti)` with `order.inputs[0].amount = 1000 USDC`, expecting `reducedAmount ≈ 999.5 USDC` to be escrowed (per `docs/content/developers/evm/intent-gateway/placing-orders.mdx:94-111`).
2. Before this transaction is mined, an admin/governance transaction calling the fee setter raises `_params.protocolFeeBps` (or sets `_destinationProtocolFees[destinationHash]`) from 5 bps to, say, 1000 bps — as exercised in `evm/tests/foundry/IntentGatewayV2Test.sol:3408-3423` (`testProtocolFeeWith10Percent`), which shows the exact same `placeOrder` code path escrowing only 900 USDC out of 1000 USDC input at 10% fee.
3. The user's `placeOrder` transaction is then mined, reading the now-updated `protocolFeeBps`. The contract computes `protocolFee = (1000e6 * 1000)/10000 = 100 USDC` and escrows only `reducedAmount = 900 USDC`, per the fee computation at `evm/src/apps/IntentGatewayV2.sol:345-346`.
4. The user receives an order committed and escrowed at 900 USDC instead of the ~999.5 USDC they intended, with no revert or refund mechanism, since `placeOrder` has no parameter allowing the caller to cap the acceptable fee or guarantee a minimum escrowed amount.

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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L348-385)
```text
        // Calculate reduced inputs (after protocol fees) for commitment and escrow
        uint256 inputsLen = order.inputs.length;
        // Use destination-specific protocol fee, fallback to source chain fee if zero
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
                uint256 protocolFee = (originalAmount * protocolFeeBps) / 10_000;
                uint256 reducedAmount = originalAmount - protocolFee;
                address token = address(uint160(uint256(order.inputs[i].token)));

                // Emit DustCollected for protocol fee if non-zero
                if (protocolFee > 0) emit DustCollected(token, protocolFee);

                reducedInputs[i] = TokenInfo({token: order.inputs[i].token, amount: reducedAmount});
                unchecked {
                    ++i;
                }
            }

            // Temporarily swap inputs to calculate commitment with reduced amounts
            TokenInfo[] memory originalInputs = order.inputs;
            order.inputs = reducedInputs;
            commitment = keccak256(abi.encode(order));
            order.inputs = originalInputs;
        } else {
            // No protocol fees, use order.inputs directly
            reducedInputs = order.inputs;
            commitment = keccak256(abi.encode(order));
        }
```

**File:** docs/content/developers/evm/intent-gateway/placing-orders.mdx (L94-115)
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

<Callout type="warn">
Do not build an order by reducing the input yourself to account for the protocol fee. Send the gross input amount and use the amounts returned by `quoteIntent()`. The quote prices the fee-reduced escrow amount; reducing it again would make the order smaller than intended.
</Callout>
```
