### Title
Tron `IntentGatewayV2.placeOrder` omits the duplicate-token validation present in the EVM contract, permitting escrow miscounting and over-release - (File: evm/tron/contracts/apps/IntentGatewayV2.sol)

### Summary
The `buy()`-style root cause in the referenced HydraDX bug (unvalidated identical `asset_in`/`asset_out` identifiers causing the AMM to compute a near-zero cost swap) has a direct analog in Hyperbridge's Intent Gateway: `placeOrder` must reject duplicate token identifiers among an order's legs so that per-token escrow accounting and per-output-token fill tracking stay sound. The canonical EVM `IntentGatewayV2.sol` enforces this with explicit duplicate-input and duplicate-output rejection logic, added specifically as a security fix. The Tron deployment of the same contract, `evm/tron/contracts/apps/IntentGatewayV2.sol`, does **not** carry these checks.

### Finding Description
In the audited/fixed EVM contract, `placeOrder` performs two validations that are absent from the Tron variant:

1. Duplicate output tokens are rejected via a transient-storage scan before escrow is created: [1](#0-0) 

2. Duplicate input tokens are rejected when crediting escrow (each token bucket must start at zero): [2](#0-1) 

These checks were added specifically to close a previously identified issue, as documented by the regression tests in the Foundry suite: [3](#0-2) [4](#0-3) 
The test comments explicitly state the regressions being guarded against: *"same-chain partial fills over-release repeated input escrow"* and *"same-chain partial fills prematurely finalize repeated output legs."*

The Tron contract's `placeOrder`, however, has neither check. Duplicate input tokens are silently merged with `+=` instead of being rejected: [5](#0-4) 
And there is no loop anywhere in `placeOrder` that rejects duplicate `order.output.assets[].token` entries — the duplicate-output guard block present in the EVM version (lines 196–211 above) is entirely missing from the Tron file.

This is functionally the same class of bug as the HydraDX report: an externally-reachable, unprivileged entry point (`placeOrder`, callable by any user) accepts a data structure with two identifier fields (input/output token legs) that are supposed to be distinct, but the contract fails to validate that constraint. Downstream logic (the same-chain partial-fill accounting keyed per output token, and the escrow bucket keyed per input token) assumes uniqueness of these keys, exactly as the stableswap `buy()` math assumed `asset_in != asset_out`.

### Impact Explanation
Per the codebase's own regression-test documentation, allowing duplicate output tokens causes same-chain partial fills to prematurely finalize a repeated output leg (a solver can trigger full-fill logic while only funding one of the duplicated legs), and allowing duplicate input tokens without proper reconciliation causes over-release of escrowed funds during partial fills. Both outcomes are direct theft-of-funds / permanent-freezing analogs: a solver (an unprivileged, permissionless actor per this protocol's design) can under-deliver output while draining the user's full escrowed input, or a user can construct an order that later causes escrow to be released in excess of what was actually locked. This maps to "concrete theft ... of funds" in the same way the original stableswap bug allowed draining pool liquidity for negligible payment.

### Likelihood Explanation
`placeOrder` is a fully permissionless, user-facing entry point with no privileged precondition — exactly the reachable surface required (intent escrow path). Constructing an order with duplicate `output.assets[].token` entries requires no special access; it is a matter of constructing the calldata. The bug class is proven to be real and exploitable in this exact codebase, since the maintainers already wrote and shipped a fix plus regression tests for the identical scenario in the mainline EVM contract — the Tron fork simply never received the corresponding fix.

### Recommendation
Port the duplicate-output-token rejection loop (EVM `IntentGatewayV2.sol` lines 196–211) and the duplicate-input-token rejection-on-credit logic (EVM lines 363–373, i.e., reverting when `_orders[commitment][token] != 0` rather than merging with `+=`) into `evm/tron/contracts/apps/IntentGatewayV2.sol`'s `placeOrder`. More generally, audit all chain-specific forks/copies of `IntentGatewayV2.sol` (Tron and any others) for divergence from the canonical, patched EVM implementation, since this indicates the Tron variant is not kept in sync with security fixes applied to the primary contract.

### Proof of Concept
Concrete reachability is demonstrated by the existing regression tests against the *fixed* EVM contract, which show the exact behavior that recurs when the checks are absent: [6](#0-5) [7](#0-6) 
Both tests call `placeOrder` with two legs pointing at the same token (USDC/USDC or DAI/DAI) and assert `vm.expectRevert(IntentsBase.InvalidInput.selector)`. Because the Tron `placeOrder` (lines 338–469) contains no equivalent revert path, submitting the same order shapes there would not revert, and the underlying escrow/partial-fill double-counting behavior the fix was designed to prevent would recur on Tron.

Note: I was unable to locate the Tron contract's `fillOrder` / partial-fill implementation within `evm/tron/contracts/**` in the available index (searches for `_partialFills`, `fillOrder`, `_fillSameChain`, `_fillCrossChain` returned no matches), so I could not directly trace the full fill-side exploitation path on the Tron deployment (e.g., confirm it uses the same `_partialFills[commitment][outputToken]` pattern). If Tron's fill/settlement logic lives in a different file not covered by my search, or if Tron does not yet expose `fillOrder`, the practical impact should be reverified against that code before treating this as fully proven end-to-end on Tron. The root-cause gap in `placeOrder`'s validation, however, is directly confirmed by file comparison.

### Citations

**File:** evm/src/apps/IntentGatewayV2.sol (L196-211)
```text

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
```

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
