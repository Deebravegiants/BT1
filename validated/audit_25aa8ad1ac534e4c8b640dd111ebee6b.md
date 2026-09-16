Confirmed: the main EVM `IntentGatewayV2.sol` correctly does before/after balance checks and mutates `order.inputs[i].amount` to the actual received amount for both the predispatch path and the direct path [1](#0-0) . The Tron deployment of the same contract, however, escrows the unadjusted `reducedInputs[i].amount` (computed from the user-specified `order.inputs[i].amount`, not the actual amount transferred) in both the predispatch and direct paths [2](#0-1) , and even where it does read `balanceOf(dispatcher)` in the predispatch path it still credits escrow with `reducedInputs[i].amount`, not the measured `balance` [3](#0-2) .

### Title
Ineffective Handling of Fee-on-Transfer/Rebasing Tokens in Tron IntentGatewayV2 Escrow Accounting - (File: evm/tron/contracts/apps/IntentGatewayV2.sol)

### Summary
The Tron variant of `IntentGatewayV2.placeOrder` escrows the user-declared input amount rather than the amount actually received by the contract, unlike the canonical EVM `IntentGatewayV2.sol`, which explicitly patched this by snapshotting balances before/after every transfer.

### Finding Description
In `placeOrder` (Tron), for the non-predispatch path, the contract calls `IERC20(token).safeTransferFrom(msg.sender, address(this), order.inputs[i].amount)` and then unconditionally credits `_orders[commitment][token] += reducedInputs[i].amount` — `reducedInputs` is derived purely from `order.inputs[i].amount` (minus protocol fee bps), with no read of the gateway's actual token balance before/after the transfer [4](#0-3) , [5](#0-4) . For a fee-on-transfer (FoT) token, or one that rebases downward while escrowed, this overstates the escrow balance recorded in `_orders[commitment][token]` relative to the tokens actually held by the contract.

The predispatch path does read `IERC20(token).balanceOf(dispatcher)` to size the sweep transfer and computes a `dust` value against `requiredAmount`, but it still credits escrow with `reducedInputs[i].amount` (the pre-fee-adjusted, user-specified figure) rather than the measured `balance` actually swept back to the gateway [3](#0-2) . If the second-hop transfer from `dispatcher` to `IntentGateway` (via the raw `IERC20.transfer` call assembled into `transferCalls`) is itself subject to a transfer fee, the amount actually received by the gateway will be less than what is credited to escrow, exactly mirroring the M-07 root cause (accounting mismatched to actual token flow).

This directly contrasts with the fix already present in the mainline EVM contract, which computes `balBefore`/`balAfter` around every `safeTransferFrom` and mutates `order.inputs[i].amount` to the delta before computing protocol fees, the commitment, and the escrow credit [6](#0-5)  — and is further validated by dedicated fee-on-transfer regression tests (`testPlaceOrder_FeeOnTransferToken_EscrowMatchesReceived`, `testPlaceOrder_FeeOnTransferToken_WithProtocolFee`, `testPlaceOrder_FeeOnTransferToken_Predispatch`) [7](#0-6) , [8](#0-7) . The Tron variant has no equivalent test or protection.

### Impact Explanation
Overstated escrow relative to actual token holdings creates a shortfall: at fill or withdrawal time, `_withdraw`/`withdraw` will attempt to transfer out amounts recorded in `_orders[commitment][token]` that exceed the gateway's real balance for that FoT/rebasing token [9](#0-8) . Depending on ordering, either the intended solver/beneficiary is under-paid (their fill is under-collateralized) or a later withdrawal from the same shared escrow reverts due to insufficient balance, freezing funds for other users relying on the same pool of escrowed input tokens. This is a permanent freezing/loss-of-funds condition for at least one party once the token's fee/rebasing behavior manifests, matching the accepted severity of the referenced report (Medium).

### Likelihood Explanation
Requires the input token configured for an order to be a fee-on-transfer or negatively-rebasing ERC20; the Intent Gateway is generic and permits arbitrary `order.inputs[i].token` addresses, so nothing on-chain prevents a user or integrator from specifying such a token. Given that the mainline EVM contract was specifically hardened against this exact scenario (with dedicated tests), it's clear FoT-token support was a known and expected usage pattern for this contract family — meaning the Tron variant's gap is reachable under normal operation, not just a contrived edge case.

### Recommendation
Port the mainline fix to the Tron contract: snapshot `IERC20(token).balanceOf(address(this))` before and after each `safeTransferFrom` (and before/after the predispatch sweep from `dispatcher`), and use the measured delta — not `order.inputs[i].amount`/`reducedInputs[i].amount` — as the basis for the escrow credit, the protocol-fee calculation, and the commitment hash, exactly mirroring `evm/src/apps/IntentGatewayV2.sol` lines 230-329.

### Proof of Concept
1. Deploy the Tron `IntentGatewayV2` with a 1% fee-on-transfer ERC20 as the input token.
2. User calls `placeOrder` with `order.inputs[0].amount = 1000e18` for the FoT token (non-predispatch path).
3. `safeTransferFrom(msg.sender, address(this), 1000e18)` delivers only `990e18` to the gateway (1% fee burned/redirected).
4. `_orders[commitment][token] += reducedInputs[0].amount` credits escrow based on `1000e18` (minus any protocol fee), i.e. up to `1000e18`, while the gateway's actual token balance increased by only `990e18`.
5. When the order is filled/withdrawn, `withdraw()` attempts to transfer the escrowed amount (`~1000e18` less protocol fee) to the beneficiary from a contract that only holds `990e18` for that token, causing either under-payment relative to what was promised or an on-chain revert/insolvency once multiple orders compete for the same shortfall, consistent with the `RoyaltyVault`/`Splitter` "last user cannot withdraw" pattern described in the source report.

### Citations

**File:** evm/src/apps/IntentGatewayV2.sol (L312-329)
```text
        } else {
            for (uint256 i; i < inputsLen;) {
                if (order.inputs[i].amount == 0) revert InvalidInput();
                address token = address(uint160(uint256(order.inputs[i].token)));
                if (token == address(0)) {
                    if (msgValue < order.inputs[i].amount) revert InsufficientNativeToken();
                    msgValue -= order.inputs[i].amount;
                } else {
                    uint256 balBefore = IERC20(token).balanceOf(address(this));
                    IERC20(token).safeTransferFrom(msg.sender, address(this), order.inputs[i].amount);
                    order.inputs[i].amount = IERC20(token).balanceOf(address(this)) - balBefore;
                }

                unchecked {
                    ++i;
                }
            }
        }
```

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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L416-446)
```text
            // Transfer tokens from call dispatcher back to IntentGateway
            Call[] memory transferCalls = new Call[](inputsLen);
            for (uint256 i; i < inputsLen;) {
                address token = address(uint160(uint256(order.inputs[i].token)));
                uint256 requiredAmount = order.inputs[i].amount;
                uint256 balance;

                if (token == address(0)) {
                    balance = address(dispatcher).balance;
                    if (balance < requiredAmount) revert InsufficientNativeToken();
                    transferCalls[i] = Call({to: address(this), value: balance, data: ""});
                } else {
                    balance = IERC20(token).balanceOf(dispatcher);
                    if (balance < requiredAmount) revert InvalidInput();
                    transferCalls[i] = Call({
                        to: token,
                        value: 0,
                        data: abi.encodeWithSelector(IERC20.transfer.selector, address(this), balance)
                    });
                }

                uint256 dust = balance - requiredAmount;
                if (dust > 0) emit DustCollected(token, dust);

                // Store reduced amount (after protocol fees) in escrow
                _orders[commitment][token] += reducedInputs[i].amount;

                unchecked {
                    ++i;
                }
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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L691-714)
```text
    function withdraw(WithdrawalRequest memory body, bool isRefund) internal {
        address beneficiary = address(uint160(uint256(body.beneficiary)));
        _filled[body.commitment] = beneficiary;

        // redeem escrowed tokens
        uint256 len = body.tokens.length;
        for (uint256 i; i < len;) {
            address token = address(uint160(uint256(body.tokens[i].token)));
            uint256 amount = body.tokens[i].amount;
            if (_orders[body.commitment][token] == 0) revert UnknownOrder();

            if (token == address(0)) {
                (bool sent,) = beneficiary.call{value: amount}("");
                if (!sent) revert InsufficientNativeToken();
            } else {
                (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
                if (!success) revert TransferFailed();
            }

            _orders[body.commitment][token] -= amount;
            unchecked {
                ++i;
            }
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

**File:** evm/tests/foundry/IntentGatewayV2SameChainTest.sol (L2625-2640)
```text
    function testPlaceOrder_FeeOnTransferToken_Predispatch() public {
        FeeOnTransferToken fot = new FeeOnTransferToken(100); // 1% transfer fee
        fot.mint(user, 10000 * 1e18);

        uint256 predispatchAmount = 1000 * 1e18;
        // After transferring to dispatcher: 1% fee = dispatcher receives 990
        uint256 dispatcherReceived = predispatchAmount - (predispatchAmount * 100) / 10000;
        // After dispatcher transfers to gateway: another 1% fee = gateway receives ~980.1
        uint256 gatewayReceived = dispatcherReceived - (dispatcherReceived * 100) / 10000;

        // Predispatch: send FOT to dispatcher, the "call" is a no-op (empty calls array)
        TokenInfo[] memory predispatchAssets = new TokenInfo[](1);
        predispatchAssets[0] = TokenInfo({token: bytes32(uint256(uint160(address(fot)))), amount: predispatchAmount});

        // The predispatch call is an empty Call[] dispatch (no-op, tokens just sit on dispatcher)
        Call[] memory emptyCalls = new Call[](0);
```
