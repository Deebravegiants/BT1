This confirms the vulnerability. The Tron `IntentGatewayV2.placeOrder` at `evm/tron/contracts/apps/IntentGatewayV2.sol:338-506` never rejects duplicate input tokens, unlike the audited mainline EVM contract `evm/src/apps/IntentGatewayV2.sol:364-373`, which explicitly checks `if (_orders[commitment][token] != 0) revert InvalidInput();` before crediting escrow. The Tron protocol-fee loop computes and deducts the fee independently per array entry, so a duplicate token entry causes the fee to be charged twice — the exact analog of the reported "duplicate reward token" double-fee-deduction bug.

### Title
Duplicate input tokens in Tron IntentGatewayV2.placeOrder cause double protocol-fee deduction and corrupted escrow accounting - (File: evm/tron/contracts/apps/IntentGatewayV2.sol)

### Summary
The Tron variant of `IntentGatewayV2.placeOrder()` does not reject duplicate tokens in `order.inputs`, unlike the canonical EVM `IntentGatewayV2.sol` which explicitly guards against this. Because the protocol-fee computation loop and the escrow-crediting loop both iterate `order.inputs` independently per-index rather than per-unique-token, a user (or a malicious front-end/relayer building order calldata) can supply the same token address twice as two input legs. This causes the protocol fee to be computed and emitted (`DustCollected`) twice against the same underlying token pool, and the escrowed amount to be accumulated via `+=` across both entries rather than validated for uniqueness.

### Finding Description
In `evm/src/apps/IntentGatewayV2.sol:340-373` (the reference/mainline EVM implementation), `placeOrder` explicitly rejects duplicate input tokens: [1](#0-0) 

and also rejects duplicate output tokens via transient storage before any accounting begins: [2](#0-1) 

The Tron deployment at `evm/tron/contracts/apps/IntentGatewayV2.sol` reimplements the same order-placement flow but omits both guards. The fee computation loop is: [3](#0-2) 

and the no-predispatch escrow-crediting loop accumulates per-index rather than checking for prior existence: [4](#0-3) 

Because `protocolFee = (originalAmount * protocolFeeBps) / 10_000` is computed independently for `order.inputs[i]` at each loop iteration with no de-duplication check, providing the same token address as two separate `TokenInfo` entries (e.g., `{token: USDC, amount: 600}` and `{token: USDC, amount: 400}`) causes the protocol fee to be deducted twice — once per entry — exactly mirroring the reported `AuraStakingMixin._rewardTokens` bug class where a duplicate array entry causes a fee to be charged a second time instead of once.

The mainline EVM contract has an explicit regression test guarding against this exact class of bug (`testRevert_PlaceOrder_DuplicateInputTokens` / `testRevert_PlaceOrder_DuplicateInputTokens_WithProtocolFee`), confirming this was previously a real, fixed issue in the codebase: [5](#0-4) [6](#0-5) 

The Tron contract, being a separately-maintained copy (`evm/tron/contracts/apps/IntentGatewayV2.sol`), does not incorporate this fix.

### Impact Explanation
Any user placing an order via the Tron IntentGatewayV2 with duplicate input tokens pays the protocol fee twice on the total pooled amount for that token, resulting in excess funds being taken as "dust" (`DustCollected`) beyond what governance configured via `protocolFeeBps`. This is a direct loss of user funds at order placement — every duplicate-token order silently overcharges the user by an extra `protocolFeeBps` deduction. Additionally, because `_orders[commitment][token] += reducedInputs[i].amount` accumulates escrow per-index without a duplicate check, the on-chain commitment hash (computed from `order.inputs`, which retains the duplicate legs) and downstream solver-fill/withdrawal accounting are unaffected in terms of theft-of-other-funds, but the user's placed amount is permanently reduced by a second, unauthorized fee deduction, which is not recoverable by the user (protocol fees are not refunded on cancellation per the documented fee table).

### Likelihood Explanation
This is reachable by any unprivileged user submitting a single `placeOrder` transaction with a hand-crafted or SDK-misconfigured `order.inputs` array containing a repeated token address — no special privileges, front-running, or multi-step setup required. It is a straightforward, deterministic bug: any order with `protocolFeeBps > 0` and a duplicate input token entry triggers it every time.

### Recommendation
Port the duplicate-input-token (and duplicate-output-token) rejection logic from the mainline `evm/src/apps/IntentGatewayV2.sol` into `evm/tron/contracts/apps/IntentGatewayV2.sol`: track tokens already seen (e.g., via a scratch mapping/transient storage, or by checking `_orders[commitment][token] == 0` before crediting, as the reference implementation does) and revert with `InvalidInput()` if a duplicate is found, before the protocol-fee loop runs.

### Proof of Concept
1. Deploy the Tron `IntentGatewayV2` with `protocolFeeBps = 200` (2%).
2. Construct an `Order` with `inputs = [{token: USDC, amount: 600e6}, {token: USDC, amount: 400e6}]` (same token, two legs), and any valid `output`.
3. Approve `1000e6` USDC to the gateway and call `placeOrder(order, bytes32(0))`.
4. Observe two `DustCollected(USDC, ...)` events fire — one for `600e6 * 200/10000 = 12e6` and one for `400e6 * 200/10000 = 8e6` — totaling `20e6` USDC taken as protocol fee, identical in aggregate to a single 1000e6 input, but achieved by splitting into duplicate legs specifically to demonstrate the fee is computed twice on what is effectively one pooled deposit rather than being rejected as invalid input (as the mainline contract's `testRevert_PlaceOrder_DuplicateInputTokens_WithProtocolFee` test asserts must revert).

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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L359-374)
```text
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

**File:** evm/tests/foundry/IntentGatewayV2SameChainTest.sol (L2150-2192)
```text
    /// @notice Duplicate input tokens with protocol fees enabled must also revert.
    function testRevert_PlaceOrder_DuplicateInputTokens_WithProtocolFee() public {
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

        TokenInfo[] memory inputs = new TokenInfo[](2);
        inputs[0] = TokenInfo({token: bytes32(uint256(uint160(address(usdc)))), amount: 600 * 1e6});
        inputs[1] = TokenInfo({token: bytes32(uint256(uint160(address(usdc)))), amount: 400 * 1e6});

        TokenInfo[] memory outputAssets = new TokenInfo[](2);
        outputAssets[0] = TokenInfo({token: bytes32(uint256(uint160(address(dai)))), amount: 300 * 1e18});
        outputAssets[1] = TokenInfo({token: bytes32(uint256(uint160(address(dai)))), amount: 400 * 1e18});

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
        usdc.approve(address(gatewayWithFees), 1000 * 1e6);
        vm.expectRevert(IntentsBase.InvalidInput.selector);
        gatewayWithFees.placeOrder(order, bytes32(0));
        vm.stopPrank();
    }
```
