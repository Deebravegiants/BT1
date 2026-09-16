### Title
Fee-on-transfer tokens (e.g. future-fee USDT) cause insolvent escrow accounting in Tron `IntentGatewayV2.placeOrder` - ([File: evm/tron/contracts/apps/IntentGatewayV2.sol])

### Summary
The Tron variant of `IntentGatewayV2.placeOrder` credits the internal escrow ledger `_orders[commitment][token]` using the user-requested (pre-fee) input amount rather than the amount actually received by the contract via `safeTransferFrom`. Unlike the canonical EVM `IntentGatewayV2` (`evm/src/apps/IntentGatewayV2.sol`), which explicitly snapshots balances before/after transfers to compute the real received amount for fee-on-transfer tokens, the Tron port omits this check entirely.

### Finding Description
In `evm/tron/contracts/apps/IntentGatewayV2.sol`, the non-predispatch escrow path does: [1](#0-0) 

`IERC20(token).safeTransferFrom(msg.sender, address(this), order.inputs[i].amount)` pulls tokens from the user, but the actual amount credited to escrow, `_orders[commitment][token] += reducedInputs[i].amount`, is derived from `order.inputs[i].amount` (the amount requested pre-transfer, only reduced by the protocol fee bps) — not from the contract's measured token balance delta. If the input `token` deducts a transfer fee (as USDT is capable of doing, per its owner-controlled fee switch, even though it is currently zero), the gateway will hold strictly less than what is recorded in `_orders`.

This is the exact bug class from the referenced report: the contract assumes `transferFrom(x)` delivers `x` tokens, and mints/credits internal accounting for the full requested amount instead of the amount actually received.

The predispatch path has the same flaw: dust is only computed relative to `requiredAmount` on the dispatcher-side balance snapshot, but the final escrow credit at line 441 still uses `reducedInputs[i].amount`, which was derived from the original (pre-any-transfer-fee) `order.inputs[i].amount`, not from what the gateway itself received after the final `transfer` call from the dispatcher — compounding potential fee losses across two hops without adjusting escrow bookkeeping: [2](#0-1) 

This directly contrasts with the fixed logic already present in the canonical EVM contract, which explicitly documents and defends against this: [3](#0-2) [4](#0-3) 

and is covered by dedicated fee-on-transfer regression tests for the main contract: [5](#0-4) 

No equivalent test or balance-delta guard exists for the Tron contract.

### Impact Explanation
Escrow entries (`_orders[commitment][token]`) represent claims that solvers and users rely on to be redeemable/fillable/refundable for the full recorded amount. If the escrowed amount exceeds the actual token balance held by the contract (because of a fee-on-transfer or future-fee-enabled token like USDT), later legitimate settlements (solver fill payouts, order cancellations/refunds, or cross-chain redemption of escrow) for that token will be undercollateralized: the contract will not hold enough tokens to honor all outstanding escrow claims. This can result in reverted/stuck withdrawals for some order participants, or (worse) a race where whichever party withdraws first drains the deficient token balance, permanently leaving other equally-entitled parties unable to redeem their escrowed funds — a direct freezing/loss of user funds, matching the "High" severity impact described in the referenced report (last users unable to withdraw due to insufficient token in contract).

### Likelihood Explanation
The affected code path is reachable by any unprivileged user calling `placeOrder` with an ERC20 input token, requiring no privileged role. While USDT itself currently charges zero fee, the contract explicitly targets support for tokens like USDT/USDC (per the referenced audit scope) and the fee can be turned on unilaterally by the token issuer at any time, or any other deployed fee-on-transfer token could be used as an input asset on Tron. The Tron contract is a maintained fork of the audited mainline `IntentGatewayV2`, and the mainline contract shows the vulnerability was previously identified and fixed there — its absence in the Tron port indicates a regression/parity gap rather than a novel unknown risk.

### Recommendation
Mirror the fix already applied in `evm/src/apps/IntentGatewayV2.sol`: before crediting `_orders[commitment][token]`, measure `IERC20(token).balanceOf(address(this))` before and after each `safeTransferFrom` call (and after the predispatch sweep `transfer` call) and use the actual received delta — not `order.inputs[i].amount` — to compute `reducedInputs[i].amount` and the escrow credit. Recompute the commitment hash consistently from the post-transfer, actually-received amounts, exactly as done in the mainline contract's Phase 1/Phase 2 split.

### Proof of Concept
1. Deploy a fee-on-transfer ERC20 (e.g. 1% fee, analogous to a fee-enabled USDT) as an input token accepted by the Tron `IntentGatewayV2`.
2. User calls `placeOrder` with `order.inputs[0] = {token: FOT, amount: 1000e18}` and `order.fees = 0`, no predispatch.
3. `safeTransferFrom(msg.sender, address(this), 1000e18)` executes; due to the 1% fee, the contract actually receives only `990e18` FOT.
4. `_orders[commitment][FOT]` is nonetheless credited with `reducedInputs[0].amount` derived from `1000e18` (minus only the protocol fee, if any) — e.g. ~`997e18` with a 30bps protocol fee — while the contract only holds `990e18`.
5. When the escrow is later paid out to a solver (fill) or refunded to the user, the contract cannot fully back the recorded `_orders` amount, causing either a revert on payout for some claimants or a race condition where the first claimant drains the deficient balance and the rest cannot withdraw — a permanent loss/freezing of funds for at least one party.

### Citations

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

**File:** evm/src/apps/IntentGatewayV2.sol (L230-234)
```text
        // Phase 1: Transfer tokens and record actual received amounts.
        // For fee-on-transfer tokens, the gateway receives less than the requested amount.
        // We mutate order.inputs to reflect actual received so the commitment and escrow
        // are consistent with what the gateway holds.
        uint256 msgValue = msg.value;
```

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
