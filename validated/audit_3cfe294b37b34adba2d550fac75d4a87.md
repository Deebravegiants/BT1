### Title
Fee-on-transfer input tokens cause escrow insolvency and permanently frozen orders in the Tron `IntentGatewayV2.placeOrder` - (File: evm/tron/contracts/apps/IntentGatewayV2.sol)

### Summary
The Tron variant of `IntentGatewayV2.placeOrder` credits the internal escrow ledger `_orders[commitment][token]` with the user-requested (fee-adjusted) input amount instead of the amount the contract actually received from `safeTransferFrom`. For a fee-on-transfer ERC20 used as an order input, this creates a permanent mismatch between the accounting ledger and the contract's real token balance, causing later `withdraw()` calls (fills, cancellations, refunds) for that token to revert because the contract does not hold enough tokens to pay out what the ledger promises.

### Finding Description
In `placeOrder`, the commitment and escrowed amounts (`reducedInputs`) are computed from `order.inputs[i].amount` *before* any token transfer occurs: [1](#0-0) 

In the non-predispatch transfer path, the contract pulls tokens with `safeTransferFrom` using the caller-specified amount, but then unconditionally credits the escrow map with `reducedInputs[i].amount` — never checking what the contract actually received: [2](#0-1) 

For a fee-on-transfer token, `IERC20(token).safeTransferFrom(msg.sender, address(this), order.inputs[i].amount)` delivers less than `order.inputs[i].amount` to the gateway, yet `_orders[commitment][token] += reducedInputs[i].amount` records the full (pre-fee) reduced amount as escrowed. The gateway's real balance of that token is now less than the sum of what its internal ledger says is owed across all orders denominated in that token.

When a solver later fills the order (or the order is cancelled/refunded), `withdraw()` reads the ledger amount and attempts to pay it out: [3](#0-2) 

Because the recorded amount exceeds the contract's actual token balance, the outbound transfer reverts (insufficient balance), permanently blocking withdrawal/fill/cancellation for that order. If several orders share the same fee-on-transfer token, the shortfall compounds and can render the whole token accounting insolvent, freezing multiple users' funds simultaneously.

Notably, the primary EVM contract was hardened against exactly this class of bug by snapshotting balances before/after transfer and mutating `order.inputs[i].amount` to the actual received amount: [4](#0-3) 
and this behavior is explicitly covered by tests using a mock `FeeOnTransferToken`: [5](#0-4) 

The Tron contract's `placeOrder`, however, was not updated with this fix, leaving the vulnerable pre-fix pattern in production for that deployment target.

### Impact Explanation
This is a direct analog to the referenced fee-on-transfer report: incorrect balance assumptions after a token transfer cause on-chain functions (`withdraw`, reached via `fillOrder`/`cancelOrder`/cross-chain `RedeemEscrow`/`RefundEscrow`) to revert, permanently freezing escrowed user/solver funds. Because the ledger can be pushed into a state where recorded liabilities exceed actual balance, this can also cause cross-order insolvency — later legitimate claimants on the same token are unable to withdraw at all, a permanent freezing-of-funds condition.

### Likelihood Explanation
Reachable from a single unprivileged `placeOrder` transaction by any user selecting a fee-on-transfer ERC20 as an input token (e.g., a deflationary or tax token, or a standard token like USDT if fee-on-transfer is ever activated, matching the exact scenario described in the source report). No special privileges, governance, or multi-step attack setup are required — only the ability to place an order with a fee-on-transfer token as input.

### Recommendation
Apply the same fix already present in `evm/src/apps/IntentGatewayV2.sol` to the Tron contract: snapshot the gateway's token balance immediately before and after each `safeTransferFrom`, and use the *actual delta* (not the caller-specified amount) both to compute the order commitment and to credit `_orders[commitment][token]`. This ensures the escrow ledger always matches on-chain balances, including in the predispatch/dispatcher sweep path.

### Proof of Concept
1. Deploy an ERC20 with a transfer fee (e.g., 1% fee-on-transfer, similar to the `FeeOnTransferToken` test mock).
2. User calls `placeOrder` on the Tron `IntentGatewayV2` with this token as `order.inputs[0]`, amount = 1000.
3. `safeTransferFrom` delivers only 990 tokens to the gateway (1% fee burned/redirected), but `_orders[commitment][token]` is credited with `reducedInputs[0].amount` computed from 1000 (minus protocol fee if any) — i.e., ~1000, not 990.
4. A second unrelated order using the same token is placed and correctly escrowed based on its own (also over-credited) ledger entry.
5. When the first order is filled/cancelled, `withdraw()` attempts to `safeTransfer` the ledger amount (~1000) out of the gateway, but the gateway's actual token balance is insufficient (only 990 was ever received, and some of that may already be owed to other orders) — the transfer reverts, permanently freezing that order's funds and potentially blocking other orders sharing the same token pool.

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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L691-700)
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

**File:** evm/tests/foundry/IntentGatewayV2SameChainTest.sol (L2441-2494)
```text
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
