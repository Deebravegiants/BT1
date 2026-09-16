### Title
Fee-on-transfer tokens cause escrow over-crediting in Tron `IntentGatewayV2.placeOrder` - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The Tron variant of `IntentGatewayV2.placeOrder` credits the `_orders` escrow mapping with the user-specified `order.inputs[i].amount` (minus protocol fee) rather than the amount actually received by the contract via `safeTransferFrom`. For fee-on-transfer (deflationary) ERC20 tokens, the contract's real token balance will be less than what is recorded as escrowed, exactly mirroring the reported Allo `_fundPool`/`increasePoolAmount` bug class.

### Finding Description
In the non-predispatch branch of `placeOrder`, the contract pulls tokens with `safeTransferFrom` using the caller-specified amount, but then unconditionally credits the escrow ledger with `reducedInputs[i].amount`, which is derived from the same caller-specified `order.inputs[i].amount` (after protocol fee), never from the token balance actually gained: [1](#0-0) 

The protocol-fee-reduced amount used for escrow accounting is computed purely from the input amount specified by the order, with no adjustment for token transfer fees: [2](#0-1) 

The predispatch branch has a partial `balance`/`requiredAmount` check for the dispatcher-to-gateway sweep, but it still credits `_orders[commitment][token] += reducedInputs[i].amount` (the requested amount, not the actual dust-adjusted amount), and the initial `msg.sender` → dispatcher leg uses `safeTransferFrom` with no balance verification at all: [3](#0-2) 

This is a real regression relative to the main EVM `IntentGatewayV2.sol`, which was explicitly hardened against this exact issue: it snapshots balances before/after each transfer and mutates `order.inputs[i].amount` to the actually-received amount before computing the commitment and crediting escrow: [4](#0-3) [5](#0-4) 

The corresponding test suite for the main EVM gateway explicitly documents and verifies this fee-on-transfer handling, confirming the intended invariant that escrow must equal actual received balance: [6](#0-5) 

The Tron gateway lacks this balance-based accounting entirely, so if a fee-on-transfer token is used as an input asset, `_orders[commitment][token]` will record more tokens than the gateway actually holds.

### Impact Explanation
This is a direct funds-accounting corruption in the intents escrow, matching the "concrete theft or permanent freezing of funds" bar. Consequences:
- When the order is later filled and the solver attempts to claim the escrowed input token, or when the order is cancelled and refunded, the contract will try to transfer an amount it does not actually hold for that specific commitment slot, causing reverts (denial of service, permanently locking part of the deposited funds) once the shortfall exceeds any slack in the shared token balance.
- Because `_orders[commitment][token]` entries are ledger accounting shared against one aggregate ERC20 balance held by the contract, an inflated escrow record for one order can allow that order's slot to be over-paid out of tokens that were actually deposited by other users/orders, leading to fund misappropriation across orders once the pool of a fee-on-transfer token is drawn down by multiple placements/fills.

### Likelihood Explanation
Likelihood is contingent on a pool/order being configured to accept a fee-on-transfer or deflationary ERC20 as an input token — a realistic scenario since `IntentGatewayV2` is a generic, permissionless, user-supplied-token intents/orders system with no restriction preventing use of such tokens as inputs. Any unprivileged user calling `placeOrder` with a fee-on-transfer token as input triggers the miscalculation; no special privileges are required.

### Recommendation
Mirror the fix already present in the main EVM `IntentGatewayV2.sol`: measure the gateway's/dispatcher's token balance immediately before and after each `safeTransferFrom`/sweep, and use the delta (actual received amount) — not the caller-specified `amount` — both for computing the commitment hash and for crediting the `_orders` escrow mapping. Apply the same balance-based approach for the predispatch dispatcher-to-gateway leg.

### Proof of Concept
1. Deploy a 1% fee-on-transfer ERC20 token and mint balance to `user`.
2. `user` calls `placeOrder` on the Tron `IntentGatewayV2` with `order.inputs[0] = {token: FOT, amount: 1000e18}` and no predispatch.
3. Inside `placeOrder`, `IERC20(token).safeTransferFrom(msg.sender, address(this), 1000e18)` executes, but due to the 1% fee the gateway's actual balance only increases by `990e18`.
4. Despite this, `_orders[commitment][token] += reducedInputs[0].amount` credits the escrow with `1000e18` (or `1000e18` minus protocol fee if configured), not `990e18`.
5. When a solver fills the order (or the user cancels), the contract attempts to pay out the recorded escrow amount (`1000e18`/reduced) but the gateway's actual FOT balance for that token is only `990e18`, causing either a revert (locked funds/DoS) or, in a multi-order scenario, draining FOT balance belonging to other unrelated orders sharing the same token, analogous to the referenced Allo `_fundPool`/`increasePoolAmount` mismatch that caused `NOT_ENOUGH_FUNDS`/insufficient-balance failures in `RFPSimpleStrategy._distribute`.

### Citations

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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L404-441)
```text
                } else {
                    IERC20(token).safeTransferFrom(msg.sender, dispatcher, amount);
                }

                unchecked {
                    ++i;
                }
            }

            // Execute the call dispatcher with predispatch call
            ICallDispatcher(dispatcher).dispatch(order.predispatch.call);

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
