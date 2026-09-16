### Title
Missing fee-on-transfer accounting in Tron `IntentGatewayV2.placeOrder` causes escrow over-crediting and eventual insolvency - (File: evm/tron/contracts/apps/IntentGatewayV2.sol)

### Summary
The Tron variant of `IntentGatewayV2.placeOrder` credits escrow using the user-specified/fee-reduced input amount instead of the amount actually received by the contract, unlike the EVM mainline implementation which measures actual balance delta to defend against fee-on-transfer tokens.

### Finding Description
In `evm/tron/contracts/apps/IntentGatewayV2.sol`, the non-predispatch escrow path pulls tokens via `safeTransferFrom` and then unconditionally credits the internal `_orders[commitment][token]` accounting with `reducedInputs[i].amount` — a value computed purely from `order.inputs[i].amount` (the user's declared amount minus the protocol fee), without ever checking the contract's actual token balance before/after the transfer: [1](#0-0) 

The predispatch branch has the same defect: it computes `dust = balance - requiredAmount` (based on the raw `dispatcher` balance sweep) but still books escrow using `reducedInputs[i].amount` derived from the originally declared `order.inputs[i].amount`, not the balance actually swept into the gateway: [2](#0-1) 

This is exactly the reported bug class — for fee-on-transfer ERC20 tokens (per the weird-erc20 catalogue referenced in the report), `IERC20(token).safeTransferFrom(msg.sender, address(this), order.inputs[i].amount)` delivers less than `order.inputs[i].amount` to the contract, so the amount actually held by the gateway is strictly less than what gets recorded in `_orders[commitment][token]`.

By contrast, the EVM mainline `IntentGatewayV2.sol` (`evm/src/apps/IntentGatewayV2.sol`) explicitly guards against this by snapshotting `balanceOf` before and after the transfer and mutating `order.inputs[i].amount` to the actual received delta before computing the commitment and escrow: [3](#0-2) 
This fix is validated by dedicated fee-on-transfer tests in the EVM test suite: [4](#0-3) 

The Tron contract lacks this balance-delta measurement entirely, meaning the fix applied to the EVM path was not ported to the Tron deployment.

### Impact Explanation
Because `_orders[commitment][token]` is a shared per-token escrow ledger across all orders placed through the gateway, over-crediting one order's escrow with tokens the contract never actually received creates a solvency gap: the sum of all `_orders[...]` balances for a token can exceed the gateway's real token balance. When solvers fill orders and the gateway later needs to release/refund escrowed funds for that token (on fill settlement, timeout refund, or cross-chain acceptance), there will be insufficient tokens to honor all outstanding order commitments. This can result in a permanent freezing of funds for other, unrelated legitimate orders sharing that token pool (later claimants cannot be paid out) — a concrete fund-freezing/accounting-insolvency impact reachable by any single unprivileged user submitting a `placeOrder` with a fee-on-transfer token.

### Likelihood Explanation
Likelihood is moderate-to-high for chains/tokens where fee-on-transfer tokens exist and are permitted as input assets. Any user can trigger this by simply placing an order with such a token — no privileged role or special conditions needed; the only requirement is a fee-on-transfer ERC20 being used as `order.inputs[i].token` on the Tron deployment.

### Recommendation
Port the same fix used in the EVM `IntentGatewayV2.sol`: snapshot `IERC20(token).balanceOf(address(this))` (or `balanceOf(dispatcher)` for the predispatch sweep) before and after each transfer, and use the actual received/swept delta — not the caller-declared amount — both for computing `reducedInputs`/the commitment hash and for crediting `_orders[commitment][token]` in `evm/tron/contracts/apps/IntentGatewayV2.sol`.

### Proof of Concept
1. Deploy the Tron `IntentGatewayV2` with a fee-on-transfer ERC20 (e.g., 1% fee) as an allowed input token.
2. User calls `placeOrder` with `order.inputs[0] = {token: FOT, amount: 1000e18}` and no predispatch.
3. `safeTransferFrom` delivers only 990e18 to the gateway (per `evm/tron/contracts/apps/IntentGatewayV2.sol:459`), but `_orders[commitment][FOT] += reducedInputs[0].amount` (`evm/tron/contracts/apps/IntentGatewayV2.sol:463`) credits an amount derived from the full 1000e18 input (minus only the protocol fee), overstating the escrow by ~10e18.
4. Repeat with multiple orders/users; the aggregate `_orders[...]` ledger for that token now exceeds the gateway's actual token balance.
5. When solvers attempt to settle/withdraw escrowed funds for later orders, transfers fail due to insufficient contract balance, permanently freezing those users' funds.

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

**File:** evm/tests/foundry/IntentGatewayV2SameChainTest.sol (L2440-2493)
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
```
