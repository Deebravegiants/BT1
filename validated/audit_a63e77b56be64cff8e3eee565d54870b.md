### Title
`fillOrder()` can be front-run by a minimal-output solver, stealing escrow from the auction-selected winner when `solverSelection` is disabled - ([File: evm/src/apps/IntentGatewayV2.sol])

### Summary
When the `IntentGatewayV2` deployment has `_params.solverSelection == false`, `fillOrder()` performs no on-chain binding between the order and any particular solver. Any address can call `fillOrder()` for a pending, unfilled order as long as it supplies at least the minimum required output amount. This reproduces the exact bug class described in the Clearpool `bid()` report: whoever's transaction lands first captures the "auction," so a watcher can front-run a legitimate, price-competitive solver's fill transaction with the bare minimum output and steal the escrowed input tokens.

### Finding Description
The Intent Gateway's off-chain auction (documented in `docs/content/developers/evm/intent-gateway/overview.mdx` and implemented via `BidManager`/`OrderExecutor` in the SDK) lets solvers submit `UserOperation` bids to the Hyperbridge coprocessor; the user/SDK picks the best bid off-chain and then a single on-chain transaction executes the fill. [1](#0-0) 

On-chain settlement is governed entirely by `fillOrder()`: [2](#0-1) 

The critical gate is:

```solidity
if (_filled[commitment] != address(0)) revert Filled();

if (_params.solverSelection) {
    bytes32 storedSelectionHash;
    assembly { storedSelectionHash := tload(commitment) }
    bytes32 expectedSelectionHash = keccak256(abi.encode(msg.sender, order.session));
    if (storedSelectionHash != expectedSelectionHash) revert Unauthorized();
}
```

This solver-binding check is **only enforced when `solverSelection` is enabled**. Test fixtures and deployment configs in this codebase explicitly configure gateways with `solverSelection: false` (e.g. `IntentGatewayV2SameChainTest.testSameChainSwap_WithProtocolFee`): [3](#0-2) 

In that mode, `fillOrder()` is a pure race: any solver can call it directly, and the only requirement is `solverAmount >= totalRequired` per output token (both in `_fillSameChain` and `_fillCrossChain`): [4](#0-3) [5](#0-4) 

Because the fill amount only needs to meet the *minimum* required output — not the best bid the user selected off-chain — an attacker observing a pending, generous `fillOrder()` transaction in the mempool (submitted by the auction-selected solver offering surplus/better price) can front-run it with an identical transaction offering only the bare minimum required output. The attacker's transaction, if it lands first, sets `_filled[commitment] = attacker`, permanently claiming the escrowed input tokens, and the legitimate winning solver's transaction reverts with `Filled()`.

This is structurally identical to the Clearpool `bid()` issue: the on-chain state transition that finalizes the "auction" (here, `fillOrder`) is a single mempool-visible transaction with no commit-reveal, no minimum-improvement requirement tied to the off-chain-selected winner, and no per-block finality step — so it is trivially front-runnable by any unprivileged actor watching the mempool.

### Impact Explanation
A front-running attacker can:
- Capture escrowed input tokens intended for the solver the user actually selected via the off-chain auction, by supplying only the protocol-minimum output instead of the competitive (often better) price the user chose.
- Do this repeatedly against any order placed on a gateway deployed with `solverSelection: false`, systematically extracting the price spread between the "best bid" and the bare minimum, which is a direct value-theft vector for both users (who receive the worse price if the front-runner's fill also succeeds first with minimum output — though the user still gets contractually guaranteed minimum output) and for the legitimately selected solver (whose fill reverts and who loses the fee/spread they would have earned).
- This constitutes unauthorized capture of escrowed funds by an entity other than the auction's intended winner, satisfying "concrete theft ... of funds" for the intents escrow/bid flow.

### Likelihood Explanation
Any unprivileged address (an "intent solver") can observe the public mempool for `fillOrder()` calls and simply resubmit a copy with a higher gas price and the minimum valid output — no special access, collusion, or unusual capital is required beyond being able to supply the required output tokens once. The only mitigating factor is that this requires the deployment to run with `solverSelection` disabled, which the codebase's own test fixtures and deployment paths show is a real, supported configuration.

### Recommendation
- Make solver-selection binding (`select()` + transient-storage commitment) mandatory rather than an optional `_params.solverSelection` toggle, so every fill is atomically bound to the solver chosen through the Hyperbridge auction and cannot be front-run by an unrelated address supplying only the minimum output.
- Alternatively, if unrestricted `fillOrder()` calls must remain supported for direct/no-auction fills, require the caller to at least match or exceed the price offered by any currently pending competing fill for the same commitment (e.g., via a reveal/commit scheme or a minimum improvement threshold), consistent with the original report's recommendation to resolve based on a prior block's best bid rather than the fastest transaction.

### Proof of Concept
1. Deploy `IntentGatewayV2` with `Params.solverSelection = false` (as done in `evm/tests/foundry/IntentGatewayV2SameChainTest.sol`).
2. User places an order requiring `outputAmount` of `DAI`, escrowing `inputAmount` of `USDC`.
3. Off-chain auction (SDK `OrderExecutor`/`BidManager`) selects "Solver B", who signs and prepares to submit `fillOrder(order, { outputs: [amount = 1000 DAI (surplus)] })`.
4. Attacker observes Solver B's pending transaction in the mempool and submits `fillOrder(order, { outputs: [amount = outputAmount exactly, i.e. minimum required] })` with a higher gas price/priority fee.
5. Attacker's transaction is mined first: `_filled[commitment]` is set to the attacker, escrowed `USDC` is transferred to the attacker.
6. Solver B's transaction reverts with `Filled()`; the user receives only the bare minimum `DAI` instead of the surplus Solver B would have provided, and Solver B loses the fill it won in the fair auction.

### Citations

**File:** docs/content/developers/evm/intent-gateway/overview.mdx (L8-10)
```text
The IntentGateway protocol enables intent-based token swaps across EVM chains connected by Hyperbridge. Users escrow tokens and declare desired outputs; solvers compete to fill orders and claim the escrowed inputs.

Each order is **auctioned** to competing solvers. Solvers bid by signing `UserOperation`s which are gas-abstracted meta-transactions and posting them to the Hyperbridge blockchain. The user reviews all bids and selects the `UserOperation` that gives them the most assets, then executes it on-chain.
```

**File:** evm/src/apps/IntentGatewayV2.sol (L443-483)
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

        address hostAddr = host();
        bytes32 currentChain = keccak256(IDispatcher(hostAddr).host());
        bytes32 orderSource = keccak256(order.source);
        bytes32 orderDest = keccak256(order.destination);
        bool isSameChain = orderSource == orderDest;

        if (isSameChain && orderSource != currentChain) revert WrongChain();
        if (!isSameChain && orderDest != currentChain) revert WrongChain();

        if (_filled[commitment] != address(0)) revert Filled();

        if (_params.solverSelection) {
            bytes32 storedSelectionHash;
            assembly {
                storedSelectionHash := tload(commitment)
            }

            bytes32 expectedSelectionHash = keccak256(abi.encode(msg.sender, order.session));
            if (storedSelectionHash != expectedSelectionHash) revert Unauthorized();
        }

        uint256 outputsLen = order.output.assets.length;
        if (options.outputs.length != outputsLen) revert InvalidInput();
        if (order.inputs.length != outputsLen) revert InvalidInput();

        if (isSameChain) {
            _fillSameChain(order, options, commitment);
        } else {
            _fillCrossChain(order, options, commitment);
        }
    }
```

**File:** evm/tests/foundry/IntentGatewayV2SameChainTest.sol (L313-324)
```text
    function testSameChainSwap_WithProtocolFee() public {
        // Deploy a new gateway with protocol fees enabled
        IntentGatewayV2 gatewayWithFees = _deployGatewayProxy();
        Params memory intentParams = Params({
            host: address(host),
            dispatcher: address(dispatcher),
            solverSelection: false,
            surplusShareBps: SURPLUS_SHARE_BPS,
            protocolFeeBps: PROTOCOL_FEE_BPS,
            priceOracle: address(0)
        });
        gatewayWithFees.initialize(intentParams, new bytes[](0), address(0));
```

**File:** evm/src/apps/intentsv2/IntrinsicIntents.sol (L65-90)
```text
        for (uint256 i; i < outputsLen; i++) {
            bytes32 outputToken = order.output.assets[i].token;
            if (options.outputs[i].token != outputToken) revert InvalidInput();

            address token = address(uint160(uint256(outputToken)));
            uint256 totalRequired = order.output.assets[i].amount;
            uint256 solverAmount = options.outputs[i].amount;

            uint256 alreadyFilled = _partialFills[commitment][outputToken];
            uint256 remaining = totalRequired - alreadyFilled;
            if (remaining == 0 || solverAmount == 0) {
                if (solverAmount == 0 && remaining > 0) isFullyFilled = false;
                continue;
            }
            uint256 fillAmount;

            uint256 beneficiaryShare = 0;
            uint256 protocolShare = 0;
            if (alreadyFilled == 0 && solverAmount > totalRequired) {
                fillAmount = totalRequired;
                (protocolShare, beneficiaryShare) =
                    _splitSurplus(solverAmount - totalRequired, order.output.call.length > 0);
            } else {
                fillAmount = solverAmount > remaining ? remaining : solverAmount;
            }

```

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L167-182)
```text
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

            if (solverAmount < totalRequired) revert InvalidInput();

```
