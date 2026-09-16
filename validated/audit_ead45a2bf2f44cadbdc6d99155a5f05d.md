### Title
Duplicate input/output token check missing in Tron `IntentGatewayV2.placeOrder`, allowing escrow to be under-collateralized / partial-fill over-release — a regression already fixed in the canonical EVM contract - ([File: evm/tron/contracts/apps/IntentGatewayV2.sol])

### Summary
The canonical EVM `IntentGatewayV2.sol` enforces two invariants in `placeOrder` before crediting escrow: no duplicate output tokens (transient-storage guard) and no duplicate input tokens (`if (_orders[commitment][token] != 0) revert InvalidInput()`), with a regression test explicitly documenting that omitting these checks previously caused "same-chain partial fills [to] over-release repeated input escrow." The Tron deployment of the same contract, `evm/tron/contracts/apps/IntentGatewayV2.sol`, is a parallel copy of `placeOrder` that omits both guards: it credits escrow with `_orders[commitment][token] += reducedInputs[i].amount` unconditionally and has no duplicate-output-token check at all. This is the same bug class as the GPToke report — an invariant enforced on one code path (`stake`/mainline `placeOrder`) is silently bypassed on a second, reachable path (`extend`/Tron `placeOrder`) that mutates the same underlying accounting.

### Finding Description
In `evm/src/apps/IntentGatewayV2.sol`, `placeOrder` (lines 194–415) enforces two duplicate-token invariants before crediting escrow:

1. Duplicate **output** tokens are rejected via a transient-storage marker loop (lines 197–221), because same-chain fills key partial-fill progress solely by output token (`_partialFills[commitment][outputToken]` in `IntrinsicIntents.sol`, lines 73–92); two output legs sharing a token would share one bucket and let a solver satisfy both legs with a single fill.
2. Duplicate **input** tokens are rejected explicitly:
```194:415:evm/src/apps/IntentGatewayV2.sol
    function placeOrder(Order memory order, bytes32 graffiti) public payable nonReentrant {
        ...
        // Phase 3: Credit escrow.
        for (uint256 i; i < inputsLen;) {
            address token = address(uint160(uint256(order.inputs[i].token)));
            // Reject duplicate input tokens
            if (_orders[commitment][token] != 0) revert InvalidInput();
            _orders[commitment][token] = reducedInputs[i].amount;
            ...
``` [1](#0-0) 

The test suite `IntentGatewayV2SameChainTest.sol` names this explicitly as a fix for an over-release bug:
```2115:2148:evm/tests/foundry/IntentGatewayV2SameChainTest.sol
    /// @notice Placing an order with duplicate input tokens must revert.
    /// Regression test for: same-chain partial fills over-release repeated input escrow.
    function testRevert_PlaceOrder_DuplicateInputTokens() public {
``` [2](#0-1) 

The Tron variant `evm/tron/contracts/apps/IntentGatewayV2.sol` is the same contract, deployed to reach the same `IntrinsicIntents`/fill logic, but its `placeOrder` never performs either check:
```338|    function placeOrder(Order memory order, bytes32 graffiti) public payable {
...
451|            for (uint256 i; i < inputsLen;) {
...
463|                _orders[commitment][token] += reducedInputs[i].amount;
``` [3](#0-2) 

There is no transient-storage duplicate-output-token guard anywhere in the Tron file's `placeOrder` (compare to lines 197–221 of the mainline contract, which have no counterpart here), and the input-side escrow write uses `+=` unconditionally rather than the mainline's "already set → revert" check.

### Impact Explanation
Any unprivileged user calling `placeOrder` on the Tron deployment can submit an order with duplicate input tokens or duplicate output tokens:
- **Duplicate output tokens**: on a same-chain fill, `_partialFills[commitment][outputToken]` in `IntrinsicIntents.sol` is keyed only by token, so two output legs of the same token collapse into one accounting bucket. A solver can satisfy what the order nominally requires as two separate legs while the escrow-release/fill logic treats it as a single smaller requirement, releasing escrow disproportionate to what was actually filled (fund theft / incorrect release), exactly the class of bug the mainline regression test guards against.
- **Duplicate input tokens**: escrow accounting for that token is merged/overwritten via `+=`, which combined with the fill-side per-output accounting can allow a filler to receive escrow release for more than they actually delivered, or allow the escrowed total recorded for a token to diverge from what solvers believe is required per input leg — leading to over-release of escrowed user funds to a solver, or under-collateralization enabling free/unbacked fills.

This satisfies the "concrete theft or permanent freezing of funds" bar via the intents escrow path (`fillOrder`/`placeOrder`), reachable from a single unprivileged `placeOrder` transaction on the Tron deployment.

### Likelihood Explanation
High. `placeOrder` is fully permissionless and callable by any user with the order's input tokens; constructing an order with a repeated token in `inputs` or `output.assets` requires no special privilege, capital beyond normal order sizing, or timing — it is a single malformed transaction. The mainline EVM contract's own regression test demonstrates this exact construction is straightforward to trigger and was previously exploitable in production code before the fix was added, and that fix was not mirrored into the Tron contract.

### Recommendation
Port the mainline `IntentGatewayV2.sol` duplicate-token protections into `evm/tron/contracts/apps/IntentGatewayV2.sol`:
1. Add the transient-storage (or equivalent persistent) guard rejecting duplicate `order.output.assets[i].token` entries before escrow accounting, mirroring lines 197–221 of the mainline contract.
2. Change the input-escrow crediting loop to revert on an already-set bucket (`if (_orders[commitment][token] != 0) revert InvalidInput();`) instead of accumulating with `+=`, mirroring lines 364–368 of the mainline contract.
3. Add regression tests for Tron mirroring `testRevert_PlaceOrder_DuplicateInputTokens`, `testRevert_PlaceOrder_DuplicateInputTokens_WithProtocolFee`, and `testRevert_PlaceOrder_DuplicateOutputTokens`.

### Proof of Concept
1. On the Tron deployment, a user calls `placeOrder` with `order.inputs` containing two entries for the same ERC-20 token (e.g., USDC amounts 600 and 400), and/or `order.output.assets` containing two entries for the same output token.
2. Because `evm/tron/contracts/apps/IntentGatewayV2.sol`'s `placeOrder` has no duplicate-token rejection, the order is accepted; escrow for that input token is recorded via `_orders[commitment][token] += reducedInputs[i].amount` (merging both legs into one value), and, if outputs are duplicated, `_partialFills[commitment][outputToken]` in the shared fill logic tracks only one bucket for what the order nominally lists as two legs.
3. A solver calling `fillOrder` can then exploit the mismatch between the order's declared per-leg amounts/outputs and the merged escrow/partial-fill accounting to obtain escrow release disproportionate to what they actually delivered — the same over-release condition the mainline EVM contract's regression test (`testRevert_PlaceOrder_DuplicateInputTokens`) was written to prevent.

Note: I could not execute this against a live Tron deployment or find a Tron-side Foundry test harness in the index to directly reproduce the over-release numerically; the PoC path is inferred from the mainline contract's identical vulnerable code shape and its documented regression test, plus confirmation that the Tron `placeOrder` lacks both fixes present upstream.

### Citations

**File:** evm/src/apps/IntentGatewayV2.sol (L364-373)
```text
        for (uint256 i; i < inputsLen;) {
            address token = address(uint160(uint256(order.inputs[i].token)));
            // Reject duplicate input tokens
            if (_orders[commitment][token] != 0) revert InvalidInput();
            _orders[commitment][token] = reducedInputs[i].amount;

            unchecked {
                ++i;
            }
        }
```

**File:** evm/tests/foundry/IntentGatewayV2SameChainTest.sol (L2115-2118)
```text
    /// @notice Placing an order with duplicate input tokens must revert.
    /// Regression test for: same-chain partial fills over-release repeated input escrow.
    function testRevert_PlaceOrder_DuplicateInputTokens() public {
        // Two input legs both using USDC — this previously merged into one escrow bucket
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L451-468)
```text
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

                unchecked {
                    ++i;
                }
            }
```
