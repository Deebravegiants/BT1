Confirmed root cause: `evm/tron/contracts/apps/IntentGatewayV2.sol`'s `placeOrder` computes the on-chain commitment using `reducedInputs`, restores `order.inputs = originalInputs` immediately after, and then emits `OrderPlaced` with `inputs: reducedInputs` while `order.destination`/other fields come from the restored `order` struct — but any caller (solver, canceller, or user) that later reconstructs an `Order` struct with the **original, pre-fee input amounts** (as escrowed/transferred amounts, or as read from any off-chain source that doesn't know about the internal fee-swap) and calls `keccak256(abi.encode(order))` in `fillOrder`/`cancelOrder` will get a *different* commitment than what was stored in `_orders[commitment]`, exactly analogous to the Guardians `Governor.cancel` hash mismatch (right root cause, wrong input to the hash).

### Title
Inconsistent Order Encoding Between `placeOrder` and `fillOrder`/`cancelOrder` Produces Unreachable Commitments - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
`placeOrder` in the Tron variant of `IntentGatewayV2` computes the order commitment (`keccak256(abi.encode(order))`) using an order struct whose `inputs` field has been temporarily swapped to `reducedInputs` (post protocol-fee amounts), then restores `order.inputs` back to the original, pre-fee amounts before returning/emitting the event. Any downstream consumer that reconstructs the `Order` struct with the original (full, pre-fee) input amounts — the natural value to use since that's what the user actually specified and paid — will compute a commitment that does not match the one actually stored in `_orders[commitment]`, `_filled[commitment]`, and the escrow accounting.

### Finding Description
In `placeOrder` ( [1](#0-0) ):
```
TokenInfo[] memory originalInputs = order.inputs;
order.inputs = reducedInputs;
commitment = keccak256(abi.encode(order));
order.inputs = originalInputs;
```
The commitment is derived from an `order` struct containing `reducedInputs`, but the struct is then reverted to `originalInputs` before any subsequent code path uses `order` again — including escrow bookkeeping (`_orders[commitment][token] += reducedInputs[i].amount`, which correctly uses `reducedInputs`) and the `OrderPlaced` event, whose `inputs: reducedInputs` field is explicitly overridden to the reduced value ( [2](#0-1) ).

The critical inconsistency is that `fillOrder` and `cancelOrder` both compute `commitment = keccak256(abi.encode(order))` directly from the caller-supplied `order` argument with no fee adjustment ( [3](#0-2)  for fill, and [4](#0-3)  for cancel). The contract nowhere persists which `inputs` values (original vs. reduced) were used for the stored commitment; it relies on solvers/cancellers to independently know to plug in the *reduced* amounts. Since `order.inputs` in the emitted event and in every natural reconstruction path (the amounts the user actually escrowed) is the *original*, pre-fee amount, any solver/canceller who builds an `Order` struct from the amounts the user paid — rather than back-computing the exact `protocolFeeBps`-derived reduced amount at the time of `placeOrder` — will produce a `commitment` that has no entry in `_orders`, causing `fillOrder`/`cancelOrder` to revert (`Filled`/`UnknownOrder`/mismatched commitment) against a hash that does not correspond to any real order.

This mirrors the reported bug class precisely: the entity that creates the canonical id (here, `placeOrder`) uses one hashing input (`reducedInputs`), while the entity that must reference that id later (`fillOrder`/`cancelOrder`) is expected to reproduce the exact same input independently, and the contract's own emitted state (`OrderPlaced.inputs`, restored `order.inputs`) does not consistently signal which value to use, creating exactly the kind of "hash of the wrong bytes" divergence that made the Guardians `cancel` call target a non-existent proposal ID.

### Impact Explanation
If a solver or the order owner naively derives `Order.inputs` from the amount the user actually deposited (the natural value visible on-chain via `Transfer`/escrow balances, or the amount specified in the frontend prior to fee deduction) rather than precisely recomputing `protocolFeeBps` at time of placement, `fillOrder` will compute a commitment for which `_filled[commitment]` and the escrow ledger `_orders[commitment]` are empty. The fill will then either revert or — worse — proceed against a *different*, uninitialized commitment slot, meaning tokens filled by the solver are never matched to the escrowed input and the user's escrowed funds under the *real* commitment remain locked, permanently frozen unless the exact reduced amount is recovered. Since `protocolFeeBps` can be updated by governance (`_params.protocolFeeBps`, `_destinationProtocolFees`) after order placement but before fill/cancel, or a destination-specific override can be introduced later, it is possible for the fee value used to reconstruct `reducedInputs` off-chain to diverge from the value in effect at `placeOrder` time, making the correct commitment unrecoverable from current state alone without replaying the exact historical parameters. This can result in permanent freezing of escrowed user funds.

### Likelihood Explanation
Likelihood is moderate to high: it triggers whenever `protocolFeeBps` (or a destination-specific fee) is nonzero — a normal operating condition — and any actor (solver, relayer-driven canceller, or the SDK if it doesn't precisely track historical fee parameters) reconstructs the order for `fillOrder`/`cancelOrder` using the pre-fee input amount rather than the exact reduced amount computed at placement time. It requires no malicious actor — an unprivileged solver or user acting in good faith following the `OrderPlaced` event's literal semantics of "the order that was placed" can trigger the mismatch.

### Recommendation
Persist the exact `Order` struct (with `reducedInputs` already applied) that was used to compute the commitment, e.g., by storing the commitment→canonical-order mapping or by requiring `fillOrder`/`cancelOrder` callers to supply the already-fee-adjusted `Order`, and make this explicit and unambiguous in the emitted `OrderPlaced` event and any indexer/SDK order-reconstruction helper, so all parties hash the identical byte-for-byte struct used to derive the on-chain commitment — matching the primary `evm/src/apps/IntentGatewayV2.sol` implementation which does not swap `order.inputs` back after committing.

### Proof of Concept
1. Governance sets `_params.protocolFeeBps = 100` (1%).
2. User calls `placeOrder` with `inputs = [{token: X, amount: 1000}]`. Contract computes `reducedInputs = [{token: X, amount: 990}]`, `commitment = keccak256(abi.encode(order_with_990))`, escrows `_orders[commitment][X] = 990`, but restores `order.inputs = [{token:X, amount:1000}]` and emits `OrderPlaced{..., inputs: reducedInputs(990)}` — so the event does show 990, but any actor who instead uses the pre-fee 1000 (e.g., from the ERC20 `Transfer` amount actually escrowed, which is 1000 since the full amount is pulled via `safeTransferFrom(msg.sender, address(this), order.inputs[i].amount)` at [5](#0-4)  using the restored `order.inputs`) reconstructs `Order{inputs:[{token:X,amount:1000}]}`.
3. Calling `fillOrder(order_with_1000, options)` computes `commitment' = keccak256(abi.encode(order_with_1000)) != commitment`. `_filled[commitment']` is zero, so the fill proceeds against a phantom commitment, crediting the solver's output transfer against a slot with no corresponding escrow — the real commitment's escrow of 990 tokens is never released to any solver and becomes permanently stuck, only recoverable by `cancelOrder`, which itself requires reconstructing the exact original `commitment` (990-input order) — information not preserved on-chain in a directly queryable form once `protocolFeeBps` has since changed.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L356-385)
```text
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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L443-463)
```text
                unchecked {
                    ++i;
                }
            }

            // Execute transfer calls from call dispatcher
            ICallDispatcher(dispatcher).dispatch(abi.encode(transferCalls));
        } else {
            for (uint256 i; i < inputsLen;) {
                if (order.inputs[i].amount == 0) revert InvalidInput();
                address token = address(uint160(uint256(order.inputs[i].token)));
                if (token == address(0)) {
                    // native token
                    if (msgValue < order.inputs[i].amount) revert InsufficientNativeToken();
                    msgValue -= order.inputs[i].amount;
                } else {
                    IERC20(token).safeTransferFrom(msg.sender, address(this), order.inputs[i].amount);
                }

                // Store reduced amount (after protocol fees) in escrow
                _orders[commitment][token] += reducedInputs[i].amount;
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L490-505)
```text
        emit OrderPlaced({
            user: order.user,
            source: order.source,
            destination: order.destination,
            deadline: order.deadline,
            nonce: order.nonce,
            fees: order.fees,
            session: order.session,
            predispatch: order.predispatch.assets,
            inputs: reducedInputs,
            beneficiary: order.output.beneficiary,
            outputs: order.output.assets,
            predispatchCall: order.predispatch.call,
            outputCall: order.output.call,
            graffiti: graffiti
        });
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L516-517)
```text
    function cancelOrder(Order calldata order, CancelOptions calldata options) public payable {
        bytes32 commitment = keccak256(abi.encode(order));
```
