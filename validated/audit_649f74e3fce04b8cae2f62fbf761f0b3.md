### Title
Fee-on-transfer / deflationary tokens break escrow accounting in Tron `IntentGatewayV2.placeOrder` - ([File: evm/tron/contracts/apps/IntentGatewayV2.sol])

### Summary
The Tron variant of `IntentGatewayV2.placeOrder` computes the escrow credit and order commitment from the user-specified `order.inputs[i].amount` and pulls tokens with a plain `safeTransferFrom`, without ever measuring the amount actually received by the contract. For fee-on-transfer/deflationary ERC20 tokens, the gateway credits `_orders[commitment][token]` with more tokens than it actually holds, exactly the bug class described in the referenced Allo `_fundPool` report.

### Finding Description
In `evm/tron/contracts/apps/IntentGatewayV2.sol::placeOrder`, the reduced (post-protocol-fee) input amounts and the commitment hash are computed directly from `order.inputs[i].amount` (the amount the user *requested* to deposit): [1](#0-0) 

Tokens are then pulled with a bare `safeTransferFrom` in the no-predispatch branch, with no balance-before/after check: [2](#0-1) 

and escrow is credited with `reducedInputs[i].amount`, i.e., a value derived from the pre-transfer-fee `order.inputs[i].amount`, not from the tokens actually deposited into the contract: [3](#0-2) 

If the input token charges a transfer fee (or rebases downward), the gateway physically receives less than `order.inputs[i].amount`, yet `_orders[commitment][token]` is credited as if the full (pre-fee) amount arrived. This is precisely the vulnerability class from the referenced report: `poolAmount`/escrow accounting is inflated relative to actual token balance held by the contract.

This is a genuine regression/divergence from the fixed logic. The main EVM `IntentGatewayV2.sol` (non-Tron) already patches this exact issue using a balance-before/after pattern that mutates `order.inputs[i].amount` to the actually-received amount before computing fees, the commitment, and the escrow credit: [4](#0-3) [5](#0-4) 

This fix (and dedicated fee-on-transfer regression tests) exists in `evm/tests/foundry/IntentGatewayV2SameChainTest.sol`: [6](#0-5) 

but the Tron contract at `evm/tron/contracts/apps/IntentGatewayV2.sol` was never updated with the same balance-check logic, leaving the deployed/deployable Tron gateway vulnerable.

### Impact Explanation
Because the intent escrow (`_orders[commitment][token]`) is a shared per-token accounting ledger backed by a single fungible token balance held by the contract, over-crediting escrow for one order creates a deficit against the contract's real token balance. When a solver fills the order (or the order is cancelled/refunded) and `withdraw`/`_withdraw` attempts to pay out the escrowed amount via `IERC20(token).safeTransfer`, the transfer can fail due to insufficient contract balance — or, if other legitimate orders' tokens are commingled, an earlier withdrawer can drain funds that were actually deposited for a later, unrelated order, causing that later order's withdrawal to permanently fail (fund freezing) or effectively steal value from other users of the same token. This is a concrete permanent-freezing/fund-accounting-insolvency issue triggerable purely by an unprivileged user submitting an order with a fee-on-transfer token via a single `placeOrder` transaction.

### Likelihood Explanation
Any user can call `placeOrder` with any ERC20 token address; the contract performs no allow-listing or fee-on-transfer detection. Fee-on-transfer and rebasing tokens are common enough in the wild that a user (accidentally) or an attacker (deliberately) can trigger the mismatch with a single transaction, making likelihood high wherever the Tron gateway accepts arbitrary ERC20 inputs.

### Recommendation
Apply the same balance-before/after measurement pattern used in the fixed EVM `IntentGatewayV2.sol` (`evm/src/apps/IntentGatewayV2.sol`) to the Tron contract: measure `IERC20(token).balanceOf(address(this))` before and after each `safeTransferFrom`, use the delta as the authoritative received amount for computing protocol fees, the order commitment, and the escrow credit, rather than trusting the caller-supplied `order.inputs[i].amount`.

### Proof of Concept
1. Deploy a fee-on-transfer ERC20 (e.g., 1% fee) and mint balance to `user`.
2. `user` calls `placeOrder` on the Tron `IntentGatewayV2` with `order.inputs[0] = {token: FOT, amount: 1000e18}`, no predispatch.
3. Contract executes `IERC20(FOT).safeTransferFrom(user, address(this), 1000e18)` — contract actually receives only 990e18 due to the transfer fee.
4. `_orders[commitment][FOT]` is nonetheless credited with `reducedInputs[0].amount` derived from 1000e18 (e.g., 1000e18 if no protocol fee, or 1000e18 minus protocol fee), i.e., 1000e18 (or close to it) — 10e18 more than the contract's real 990e18 balance for that token.
5. When the order is filled/cancelled and `withdraw` attempts `IERC20(FOT).safeTransfer(beneficiary, 1000e18)` (or the corresponding reduced amount), the transfer reverts or drains balance backing other orders, demonstrating the insolvency/freezing condition — mirroring `testPlaceOrder_FeeOnTransferToken_EscrowMatchesReceived` in `evm/tests/foundry/IntentGatewayV2SameChainTest.sol` which shows what *correct* behavior looks like on the patched EVM contract, absent here in the Tron contract.

### Citations

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
