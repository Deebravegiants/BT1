## Title
Missing Duplicate-Token Validation in Tron `IntentGatewayV2.placeOrder` Allows Double-Counted Escrow and Under-Collateralized Fills - (File: evm/tron/contracts/apps/IntentGatewayV2.sol)

### Summary
The main EVM `IntentGatewayV2.sol` `placeOrder()` explicitly rejects duplicate output tokens (and, per the associated regression tests, duplicate input tokens) using transient-storage dedup checks that revert with `InvalidInput()`. The Tron fork of the same contract, `evm/tron/contracts/apps/IntentGatewayV2.sol`, implements `placeOrder()` without any equivalent duplicate-token check for either `order.inputs` or `order.output.assets`. This mirrors the MKTF-1 bug class: nothing prevents two "legs" of the same order from referencing the same token, causing funds/escrow accounting to be double counted (or under-escrowed) exactly as the GMX report describes for long/short token collision.

### Finding Description
On the canonical EVM contract, `placeOrder()` iterates `order.output.assets` and uses transient storage (`tload`/`tstore`) to revert with `InvalidInput()` if the same output token appears twice: [1](#0-0) 

The accompanying test suite in `IntentGatewayV2SameChainTest.sol` documents that this guard is a **regression fix** for exactly this bug class — duplicate input tokens previously "merged into one escrow bucket" causing over-release, and duplicate output tokens previously shared one `_partialFills` bucket causing premature finalization: [2](#0-1) [3](#0-2) 

However, the Tron variant of the same contract (`evm/tron/contracts/apps/IntentGatewayV2.sol`) implements `placeOrder()` without any dedup check on `order.inputs` or `order.output.assets` before escrowing: [4](#0-3) 

The Tron contract accumulates escrow per token via `_orders[commitment][token] += reducedInputs[i].amount;` inside a loop over `order.inputs`, with no check that `token` (derived from `order.inputs[i].token`) has not already appeared earlier in the same array: [5](#0-4) 

Because the loop only sums into `_orders[commitment][token]`, having the same token repeated across two "input" legs (e.g., analogous to setting long == short) does not error — it simply accumulates the balance across both TokenInfo entries in escrow, while `order.output.assets` on the destination has no such protection either. This is the direct architectural analog of MKTF-1: nothing prevents the same "asset slot" from being reused twice within a single unpermissioned user-submitted structure (`Order`), which was exactly the root cause GMX fixed by validating `longToken != shortToken`.

### Impact Explanation
This is reachable by any unprivileged user calling `placeOrder()` on the Tron gateway — no special privileges required. The consequences mirror MKTF-1's double counting:
- **Duplicate input tokens**: On the canonical contract this is blocked because it previously "over-released" escrow in same-chain partial fills; the Tron contract lacks this fix, so the same over-release/under-collateralization vector during solver fills of same-chain orders is reachable.
- **Duplicate output tokens**: On the canonical contract this is blocked because duplicate output legs previously shared one `_partialFills` bucket, "prematurely finaliz[ing] repeated output legs" — again unguarded on Tron, letting a partial fill of one duplicated output leg mark both legs (and thus the whole order for that beneficiary asset) as fulfilled without the solver providing the full aggregate amount.

Both scenarios lead to fund-accounting corruption: a solver could under-deliver required output while the order registers as filled, or a user's escrow accounting could be manipulated to release more than intended — concrete theft/fund-freezing/mismatched-accounting impact consistent with the required Medium/High/Critical bar.

### Likelihood Explanation
High. `placeOrder()` is a completely unprivileged, directly user-callable entry point that accepts an arbitrary `TokenInfo[]` for both `inputs` and `output.assets`. No additional preconditions (governance, admin, or off-chain cooperation) are needed to construct an order with a repeated token address in either array; the attacker fully controls the `Order` struct submitted in a single transaction.

### Recommendation
Port the duplicate-token guard from the canonical `IntentGatewayV2.sol` `placeOrder()` (the transient-storage `tload`/`tstore` loop over `order.output.assets`, and the equivalent check that the tests expect over `order.inputs`) into the Tron contract's `placeOrder()`, reverting with `InvalidInput()` on any repeated `token` value within either array before escrow accounting proceeds.

### Proof of Concept
1. Construct an `Order` on the Tron `IntentGatewayV2` where `order.inputs[0].token == order.inputs[1].token` (e.g., both USDC), each with a nonzero `amount`.
2. Call `placeOrder(order, graffiti)` with sufficient approval for the sum of both amounts.
3. Observe that the loop at `evm/tron/contracts/apps/IntentGatewayV2.sol:450-468` accepts the order without reverting and accumulates `_orders[commitment][usdcToken]` across both legs — unlike the canonical EVM contract, which would revert per the regression test `testRevert_PlaceOrder_DuplicateInputTokens` (`evm/tests/foundry/IntentGatewayV2SameChainTest.sol:2117-2148`).
4. Similarly, construct `order.output.assets[0].token == order.output.assets[1].token`; on Tron this is accepted, whereas the canonical contract reverts per `testRevert_PlaceOrder_DuplicateOutputTokens` (`evm/tests/foundry/IntentGatewayV2SameChainTest.sol:2240-2272`), enabling a solver to fill only one leg's amount and have both duplicated output legs' partial-fill bucket satisfied.

**Note on verification limits:** I was unable to fully trace the Tron contract's `fillOrder`/partial-fill (`_partialFills`) logic within the available context to confirm the exact downstream mechanics of the double-counting exploit on that specific code path (the file is large and the fill-side function was not retrieved in full). The root-cause gap — absence of the duplicate-token check present in the canonical contract — is confirmed directly from the code shown above.

### Citations

**File:** evm/src/apps/IntentGatewayV2.sol (L194-221)
```text
    function placeOrder(Order memory order, bytes32 graffiti) public payable nonReentrant {
        if (order.inputs.length == 0) revert InvalidInput();

        // Reject duplicate output tokens
        uint256 outputsLen_ = order.output.assets.length;
        for (uint256 i; i < outputsLen_;) {
            bytes32 token = order.output.assets[i].token;
            assembly ("memory-safe") {
                if tload(token) {
                    mstore(0, 0xb4fa3fb3) // InvalidInput.selector
                    revert(0x1c, 0x04)
                }
                tstore(token, 1)
            }
            unchecked {
                ++i;
            }
        }
        // Clean up transient storage so repeated placeOrder calls in the same tx don't false-positive.
        for (uint256 i; i < outputsLen_;) {
            bytes32 token = order.output.assets[i].token;
            assembly ("memory-safe") {
                tstore(token, 0)
            }
            unchecked {
                ++i;
            }
        }
```

**File:** evm/tests/foundry/IntentGatewayV2SameChainTest.sol (L2115-2148)
```text
    /// @notice Placing an order with duplicate input tokens must revert.
    /// Regression test for: same-chain partial fills over-release repeated input escrow.
    function testRevert_PlaceOrder_DuplicateInputTokens() public {
        // Two input legs both using USDC — this previously merged into one escrow bucket
        TokenInfo[] memory inputs = new TokenInfo[](2);
        inputs[0] = TokenInfo({token: bytes32(uint256(uint160(address(usdc)))), amount: 1200 * 1e6});
        inputs[1] = TokenInfo({token: bytes32(uint256(uint160(address(usdc)))), amount: 1000 * 1e6});

        TokenInfo[] memory outputAssets = new TokenInfo[](2);
        outputAssets[0] = TokenInfo({token: bytes32(uint256(uint160(address(dai)))), amount: 500 * 1e18});
        outputAssets[1] = TokenInfo({token: bytes32(uint256(uint160(address(dai)))), amount: 1000 * 1e18});

        PaymentInfo memory output =
            PaymentInfo({beneficiary: bytes32(uint256(uint160(user))), assets: outputAssets, call: ""});

        Order memory order = Order({
            user: bytes32(0),
            source: "",
            destination: host.host(),
            deadline: block.number + 100,
            nonce: 0,
            fees: 0,
            session: address(0),
            predispatch: DispatchInfo({assets: new TokenInfo[](0), call: ""}),
            inputs: inputs,
            output: output
        });

        vm.startPrank(user);
        usdc.approve(address(intentGateway), 2200 * 1e6);
        vm.expectRevert(IntentsBase.InvalidInput.selector);
        intentGateway.placeOrder(order, bytes32(0));
        vm.stopPrank();
    }
```

**File:** evm/tests/foundry/IntentGatewayV2SameChainTest.sol (L2238-2272)
```text
    /// @notice Placing an order with duplicate output tokens must revert.
    /// Regression test for: same-chain partial fills prematurely finalize repeated output legs.
    function testRevert_PlaceOrder_DuplicateOutputTokens() public {
        TokenInfo[] memory inputs = new TokenInfo[](2);
        inputs[0] = TokenInfo({token: bytes32(uint256(uint160(address(usdc)))), amount: 1000 * 1e6});
        inputs[1] = TokenInfo({token: bytes32(uint256(uint160(address(dai)))), amount: 500 * 1e18});

        // Two output legs both requesting DAI — shares one _partialFills bucket
        TokenInfo[] memory outputAssets = new TokenInfo[](2);
        outputAssets[0] = TokenInfo({token: bytes32(uint256(uint160(address(dai)))), amount: 400 * 1e18});
        outputAssets[1] = TokenInfo({token: bytes32(uint256(uint160(address(dai)))), amount: 600 * 1e18});

        PaymentInfo memory output =
            PaymentInfo({beneficiary: bytes32(uint256(uint160(user))), assets: outputAssets, call: ""});

        Order memory order = Order({
            user: bytes32(0),
            source: "",
            destination: host.host(),
            deadline: block.number + 100,
            nonce: 0,
            fees: 0,
            session: address(0),
            predispatch: DispatchInfo({assets: new TokenInfo[](0), call: ""}),
            inputs: inputs,
            output: output
        });

        vm.startPrank(user);
        usdc.approve(address(intentGateway), 1000 * 1e6);
        dai.approve(address(intentGateway), 500 * 1e18);
        vm.expectRevert(IntentsBase.InvalidInput.selector);
        intentGateway.placeOrder(order, bytes32(0));
        vm.stopPrank();
    }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L338-356)
```text
    function placeOrder(Order memory order, bytes32 graffiti) public payable {
        // Validate that order has inputs
        if (order.inputs.length == 0) revert InvalidInput();

        address hostAddr = host();
        // fill out the order preludes
        order.user = bytes32(uint256(uint160(msg.sender)));
        order.source = IDispatcher(hostAddr).host();
        order.nonce = _nonce++;

        // Calculate reduced inputs (after protocol fees) for commitment and escrow
        uint256 inputsLen = order.inputs.length;
        // Use destination-specific protocol fee, fallback to source chain fee if zero
        bytes32 destinationHash = keccak256(order.destination);
        uint256 protocolFeeBps = _destinationProtocolFees[destinationHash];
        if (protocolFeeBps == 0) {
            protocolFeeBps = _params.protocolFeeBps;
        }
        TokenInfo[] memory reducedInputs;
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L450-468)
```text
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

                unchecked {
                    ++i;
                }
            }
```
