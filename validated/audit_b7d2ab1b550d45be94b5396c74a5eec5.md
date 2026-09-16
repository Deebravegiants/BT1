Based on my investigation, I found a concrete analog. The main EVM `IntentGatewayV2` was explicitly hardened against fee-on-transfer tokens (balance-before/after accounting), but the **Tron variant duplicates the vulnerable pattern** described in the report.

### Title
Fee-on-transfer input tokens cause escrow over-crediting in Tron `IntentGatewayV2.placeOrder`, leading to stuck/insolvent order withdrawals - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
In the primary EVM implementation, `placeOrder` in `evm/src/apps/IntentGatewayV2.sol` measures the gateway's actual token balance before and after `safeTransferFrom` and mutates `order.inputs[i].amount` to the **actually received** amount before crediting escrow and computing the commitment hash [1](#0-0) . This correctly accounts for fee-on-transfer (FOT) tokens, as validated by dedicated tests (`testPlaceOrder_FeeOnTransferToken_EscrowMatchesReceived`, `testPlaceAndFill_FeeOnTransferToken_RoundTrip`, etc.) [2](#0-1) [3](#0-2) .

However, the Tron port of the same contract, `evm/tron/contracts/apps/IntentGatewayV2.sol`, does **not** carry this fix. In its `placeOrder`, `reducedInputs` (the amount later credited to escrow) is computed from `order.inputs[i].amount` — the caller-supplied, pre-transfer amount — before any token movement occurs [4](#0-3) . In the non-predispatch branch (the common path), the contract then calls `safeTransferFrom(msg.sender, address(this), order.inputs[i].amount)` without checking the actual balance delta, and unconditionally credits `_orders[commitment][token] += reducedInputs[i].amount`, i.e. the pre-fee amount minus protocol fee, not the amount actually received: [5](#0-4) 

### Finding Description
For any ERC-20 input token that charges a transfer fee (deflationary/fee-on-transfer tokens), the Tron `IntentGatewayV2` contract will receive strictly less than `order.inputs[i].amount` due to the token's internal fee deduction, yet it credits the escrow ledger (`_orders[commitment][token]`) with a value derived from the full pre-fee amount (`reducedInputs[i].amount = originalAmount - protocolFee`, where `originalAmount` is the un-adjusted, user-specified amount) [4](#0-3) . This creates a permanent accounting mismatch between the on-chain token balance actually held by the gateway and the sum of amounts recorded as owed across all commitments for that token — exactly the root cause identified in the referenced Teller `CollateralEscrowV1` report, where withdrawal `transfer` calls for the recorded (but never-actually-held) amount will revert once the shortfall is exposed, since the contract's real token balance is insufficient to satisfy all outstanding escrow claims for that token.

### Impact Explanation
Because escrow bookkeeping overstates the true balance held for the affected token, downstream redemption/fill flows (`RedeemEscrow` withdrawal to the solver/filler, or order cancellation refund to the user) that transfer the full recorded amount will fail once the shortfall is exhausted, or in shared-pool per-token balances, will silently consume value belonging to other, unrelated orders using the same token. Either outcome is a permanent freezing of user/solver funds or an unauthorized redistribution of escrowed collateral across orders, which is a High severity, direct-loss/freezing bug reachable by a single unprivileged user simply calling `placeOrder` with a deflationary token as input.

### Likelihood Explanation
Likelihood is high for any deployment of the Tron gateway that accepts an arbitrary/whitelisted ERC-20 as an input token, since fee-on-transfer and deflationary tokens are common on-chain, and nothing in `placeOrder` (Tron variant) prevents or detects such tokens — unlike the main EVM contract, which explicitly measures actual received balance for this exact purpose [6](#0-5) . Triggering the bug requires no special privileges — just placing one order with a FOT token.

### Recommendation
Apply the same balance-delta pattern used in `evm/src/apps/IntentGatewayV2.sol` (lines 320-322 and 260-311 for the predispatch sweep) to the Tron contract: snapshot `IERC20(token).balanceOf(address(this))` before `safeTransferFrom`, compute `received = balanceAfter - balanceBefore`, mutate `order.inputs[i].amount` (and thus `reducedInputs`) to `received` before computing the commitment hash and crediting `_orders[commitment][token]`, so the escrow ledger always reflects tokens the contract actually holds.

### Proof of Concept
1. Deploy `evm/tron/contracts/apps/IntentGatewayV2.sol` with a 1% fee-on-transfer ERC-20 as an allowed input token.
2. User calls `placeOrder` with `inputs[0].amount = 1000e18` of the FOT token; user approves 1000e18.
3. `safeTransferFrom` moves 1000e18 from user, but the gateway only receives 990e18 (1% burned/redirected by the token) [7](#0-6) .
4. `_orders[commitment][token]` is credited with `reducedInputs[0].amount`, computed from the full 1000e18 (minus protocol fee only), e.g. ~997e18 if protocol fee is 0.3%, while the gateway's real balance for that token is only 990e18 [8](#0-7) [9](#0-8) .
5. When the solver/filler attempts to redeem the escrow for the recorded 997e18, the token transfer reverts (insufficient balance) or, if other orders share the token pool, drains balance belonging to unrelated commitments — resulting in stuck or misappropriated funds.

Note: I was unable to view the exact `RedeemEscrow`/withdrawal transfer code in the Tron file within the available tool budget (grep confirmed `RedeemEscrow` appears 4 times in that file), so the exact downstream failure mode (revert vs. cross-order fund leakage) could not be pinned to specific line numbers — but the root-cause over-crediting in `placeOrder` is confirmed directly from the code.

### Citations

**File:** evm/src/apps/IntentGatewayV2.sol (L230-233)
```text
        // Phase 1: Transfer tokens and record actual received amounts.
        // For fee-on-transfer tokens, the gateway receives less than the requested amount.
        // We mutate order.inputs to reflect actual received so the commitment and escrow
        // are consistent with what the gateway holds.
```

**File:** evm/src/apps/IntentGatewayV2.sol (L319-323)
```text
                } else {
                    uint256 balBefore = IERC20(token).balanceOf(address(this));
                    IERC20(token).safeTransferFrom(msg.sender, address(this), order.inputs[i].amount);
                    order.inputs[i].amount = IERC20(token).balanceOf(address(this)) - balBefore;
                }
```

**File:** evm/tests/foundry/IntentGatewayV2SameChainTest.sol (L2440-2494)
```text
    /// @notice Escrow correctly reflects actual received amount for fee-on-transfer tokens.
    function testPlaceOrder_FeeOnTransferToken_EscrowMatchesReceived() public {
        // Deploy a 1% fee-on-transfer token
        FeeOnTransferToken fot = new FeeOnTransferToken(100); // 1% = 100 bps
        fot.mint(user, 10000 * 1e18);

        uint256 inputAmount = 1000 * 1e18;
        uint256 expectedReceived = inputAmount - (inputAmount * 100) / 10000; // 990

        TokenInfo[] memory inputs = new TokenInfo[](1);
        inputs[0] = TokenInfo({token: bytes32(uint256(uint160(address(fot)))), amount: inputAmount});

        TokenInfo[] memory outputAssets = new TokenInfo[](1);
        outputAssets[0] = TokenInfo({token: bytes32(uint256(uint160(address(dai)))), amount: 900 * 1e18});

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
        fot.approve(address(intentGateway), inputAmount);
        intentGateway.placeOrder(order, bytes32(0));
        vm.stopPrank();

        // Gateway should hold only what it actually received
        assertEq(
            fot.balanceOf(address(intentGateway)), expectedReceived, "Gateway balance should match received amount"
        );

        // Reconstruct the order as placeOrder would have mutated it
        order.user = bytes32(uint256(uint160(user)));
        order.source = host.host();
        order.nonce = 0;
        order.inputs[0].amount = expectedReceived;
        bytes32 commitment = keccak256(abi.encode(order));

        // Escrow should match actual received, not the user-specified amount
        assertEq(
            intentGateway._orders(commitment, address(fot)),
            expectedReceived,
            "Escrow should equal actual received amount"
        );
    }
```

**File:** evm/tests/foundry/IntentGatewayV2SameChainTest.sol (L2558-2622)
```text
    /// @notice Full round-trip: place with fee-on-transfer, fill, solver withdraws exact escrow.
    function testPlaceAndFill_FeeOnTransferToken_RoundTrip() public {
        FeeOnTransferToken fot = new FeeOnTransferToken(100); // 1% transfer fee
        fot.mint(user, 10000 * 1e18);

        uint256 inputAmount = 1000 * 1e18;
        uint256 receivedByGateway = inputAmount - (inputAmount * 100) / 10000; // 990
        uint256 outputAmount = 900 * 1e18;

        TokenInfo[] memory inputs = new TokenInfo[](1);
        inputs[0] = TokenInfo({token: bytes32(uint256(uint160(address(fot)))), amount: inputAmount});

        TokenInfo[] memory outputAssets = new TokenInfo[](1);
        outputAssets[0] = TokenInfo({token: bytes32(uint256(uint160(address(dai)))), amount: outputAmount});

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

        // Place order
        vm.startPrank(user);
        fot.approve(address(intentGateway), inputAmount);
        intentGateway.placeOrder(order, bytes32(0));
        vm.stopPrank();

        // Reconstruct order as placeOrder mutated it
        order.user = bytes32(uint256(uint160(user)));
        order.source = host.host();
        order.nonce = 0;
        order.inputs[0].amount = receivedByGateway; // actual received

        // Solver fills
        uint256 solverFotBefore = fot.balanceOf(solver);

        vm.startPrank(solver);
        dai.approve(address(intentGateway), outputAmount);

        TokenInfo[] memory solverOutputs = new TokenInfo[](1);
        solverOutputs[0] = TokenInfo({token: bytes32(uint256(uint160(address(dai)))), amount: outputAmount});

        intentGateway.fillOrder(
            order, FillOptions({relayerFee: 0, nativeDispatchFee: 0, validUntil: 0, outputs: solverOutputs})
        );
        vm.stopPrank();

        // Solver should receive the escrowed FOT (with transfer fee applied on the way out)
        uint256 solverFotReceived = fot.balanceOf(solver) - solverFotBefore;
        uint256 expectedSolverReceived = receivedByGateway - (receivedByGateway * 100) / 10000; // 990 - 1% fee
        assertEq(solverFotReceived, expectedSolverReceived, "Solver should receive escrowed FOT minus transfer fee");

        // Gateway should have zero FOT left
        assertEq(fot.balanceOf(address(intentGateway)), 0, "Gateway should have no FOT remaining");
    }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L359-385)
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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L450-469)
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
        }
```
