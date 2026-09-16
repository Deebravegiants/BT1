### Title
Unbounded order deadlines let escrowed volatile-asset intents drift far from fill-time market price - ([File: evm/src/apps/intentsv2/IntrinsicIntents.sol])

### Summary
The reported ETH-volatility issue (price moves between request submission and off-chain fulfillment, letting one party profit and the other lose money) has a direct analog in `IntentGatewayV2`'s order-escrow flow. A user places an order escrowing input tokens — which can be `address(0)` native ETH — for a *fixed* amount of output tokens, but `order.deadline` is entirely user/placer-controlled with no protocol-enforced ceiling, so the order can remain fillable long after the escrowed asset's market price has moved.

### Finding Description
`placeOrder` escrows `order.inputs` (any ERC20 or native ETH, `token == address(0)`) against a committed, fixed `order.output.assets` amount [1](#0-0) . The pricing relationship between input and output is fixed at placement time and never revisited before fill.

`fillOrder` only checks that the order has not expired (`order.deadline >= blockNumber`) and, separately, an optional solver-supplied `options.validUntil` that bounds only how long *the solver's own bid* stands — it does nothing to bound how long the *order itself* can sit open [2](#0-1) . The test suite explicitly documents this design: "a solver's quote is a firm price the order placer may take up whenever they choose — `order.deadline` is placer-controlled with no ceiling" and "`validUntil` is the solver's own bound on how long that price stands" [3](#0-2) . A `validUntil` of `0` (unbounded) is the accepted default for direct solver fills [4](#0-3) .

At fill time, the exact escrowed input is released to the filling solver at the exchange rate fixed when the order was placed, with no re-check against current market prices — see the same-chain escrow release `escrowedAmount = order.inputs[i].amount * fillAmount / totalRequired` [5](#0-4) , and the analogous cross-chain path in `ExtrinsicIntents.sol` [6](#0-5) .

This reproduces both failure modes from the external report, but at the escrow layer instead of a gift-card fulfiller:
- **Scenario A (input asset appreciates):** A user escrows ETH (or any volatile token) as `order.inputs[0]` for a fixed output amount of a stablecoin. If ETH's price rises materially before any solver fills, the fixed output the solver must pay is now cheap relative to the ETH they receive — the solver captures the appreciation as pure arbitrage, at the user's expense, with no re-pricing or partial-refund mechanism.
- **Scenario B (input asset depreciates):** If ETH's price falls, no rational solver will fill the order (they'd be paying more in output value than the escrowed ETH is worth), so the order simply sits unfilled indefinitely (deadline has no ceiling) until the user notices and pays gas to `cancelOrder`. This mirrors the report's "cancellation is forced" scenario, except here the funds are locked in escrow for however long the placer's uncapped `deadline` allows, rather than fixed by a fulfiller's off-chain decision window.

### Impact Explanation
This is not a hypothetical: the contract explicitly supports native ETH as an escrowed input (`token == address(0)` paths in both `_fillSameChain` and `_fillCrossChain`, and tests exercising "Native ETH surplus accounting"), and enforces no maximum order lifetime. A user (or an integrator building a UI atop the SDK) who sets a generous deadline for better fill probability is unknowingly exposing the full value of their volatile-asset escrow to price drift, with no slippage/repricing protection at the protocol layer — the same class of value-extraction/loss the external report flagged for the fulfillment-based (off-chain) system, but here it can result in permanent value transfer once a solver actually executes the stale-priced fill (Scenario A) or dead capital until manual cancellation (Scenario B).

### Likelihood Explanation
Likelihood is Medium: it requires (1) a user or integrator to set a long `order.deadline` while escrowing a volatile asset, and (2) sufficient price movement in that window. Given `validUntil = 0` (unbounded) is the accepted default and no protocol constant caps `order.deadline`, this is easy to hit unintentionally through normal SDK usage rather than requiring an adversarial setup — any solver/filler that monitors open orders is naturally incentivized to exploit favorable drift the moment it appears (this is literally MEV against stale intents).

### Recommendation
- Enforce a protocol-level maximum window between order placement and `order.deadline` (e.g., a configurable `maxOrderLifetimeBlocks` checked in `placeOrder`), especially for orders whose `inputs` or `output.assets` include volatile/non-stable tokens.
- Consider requiring orders with native/volatile-asset inputs to carry an oracle-referenced bound, or a mandatory `validUntil`-style cap enforced against the order itself (not just the solver's bid) so stale intents cannot be filled far from the price at which they were placed.
- Alternatively, document and default SDKs/integrators toward short deadlines for volatile-asset orders, and consider a partial "auto-cancel" or fee-adjustment mechanism analogous to the "swap fee" the client introduced elsewhere in the codebase for volatility mitigation.

### Proof of Concept
1. User calls `placeOrder` escrowing 1 ETH (`order.inputs[0].token == address(0)`, `amount = 1 ether`) for `order.output.assets[0] = 3000 USDC`, with `order.deadline = block.number + 500_000` (far future, permitted since there is no ceiling check) — see escrow crediting logic [1](#0-0) .
2. No solver finds it profitable to fill while ETH trades near $3000.
3. Weeks later, ETH price rises to $4500. A solver calls `fillOrder` with `validUntil = 0` (unbounded, the standard default per test comments [7](#0-6) ), providing exactly 3000 USDC and receiving the full 1 ETH escrow via `escrowedAmount = order.inputs[i].amount * fillAmount / totalRequired` [5](#0-4) .
4. The solver nets ~$1500 of pure price-drift arbitrage that has nothing to do with providing a competitive swap rate — the same value-transfer mechanic described in the external ETH-slippage report, reproduced in Hyperbridge's intent-escrow surface.

### Citations

**File:** evm/src/apps/IntentGatewayV2.sol (L363-373)
```text
        // Phase 3: Credit escrow.
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

**File:** evm/src/apps/IntentGatewayV2.sol (L443-451)
```text
    function fillOrder(Order calldata order, FillOptions calldata options) public payable nonReentrant {
        uint256 blockNumber = _blockNumber();
        if (order.deadline < blockNumber) revert Expired();
        // The solver's own bound on how long its quoted price stands. Zero means unbounded,
        // which is the right default for a solver filling directly — it is only at risk from
        // its own staleness. It matters for a bid signed through the coprocessor, where the
        // order placer chooses the moment of execution and nothing else caps the wait.
        if (options.validUntil != 0 && blockNumber > options.validUntil) revert FillExpired();
        bytes32 commitment = keccak256(abi.encode(order));
```

**File:** evm/tests/foundry/IntentGatewayV2SameChainTest.sol (L155-157)
```text
    /// @dev A solver's quote is a firm price the order placer may take up whenever they
    ///      choose — `order.deadline` is placer-controlled with no ceiling. `validUntil`
    ///      is the solver's own bound on how long that price stands.
```

**File:** evm/tests/foundry/IntentGatewayV2SameChainTest.sol (L203-211)
```text
    /// @dev Zero means unbounded, which is the right default for a solver filling directly:
    ///      it is only exposed to its own staleness. Every existing caller relies on this.
    function testFillOptions_ValidUntil_ZeroIsUnbounded() public {
        uint256 inputAmount = 1000 * 1e6;
        uint256 outputAmount = 900 * 1e18;
        Order memory order = _placeSameChainOrder(inputAmount, outputAmount, 0);

        vm.roll(block.number + 500);

```

**File:** evm/src/apps/intentsv2/IntrinsicIntents.sol (L111-118)
```text
            uint256 escrowedAmount;
            if (amountFilled == totalRequired) {
                escrowedAmount = _orders[commitment][address(uint160(uint256(order.inputs[i].token)))];
            } else {
                escrowedAmount = (order.inputs[i].amount * fillAmount) / totalRequired;
            }
            escrowedInputs[i] = TokenInfo({token: order.inputs[i].token, amount: escrowedAmount});
            outputFills[i] = TokenInfo({token: outputToken, amount: fillAmount});
```

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L164-180)
```text
    function _fillCrossChain(Order calldata order, FillOptions calldata options, bytes32 commitment) internal {
        uint256 outputsLen = order.output.assets.length;

        _filled[commitment] = msg.sender;

        uint256 msgValue = msg.value;
        address beneficiary = address(uint160(uint256(order.output.beneficiary)));
        TokenInfo[] memory outputFills = new TokenInfo[](outputsLen);

        for (uint256 i; i < outputsLen; i++) {
            bytes32 outputToken = order.output.assets[i].token;
            if (options.outputs[i].token != outputToken) revert InvalidInput();

            address token = address(uint160(uint256(outputToken)));
            uint256 totalRequired = order.output.assets[i].amount;
            uint256 solverAmount = options.outputs[i].amount;

```
