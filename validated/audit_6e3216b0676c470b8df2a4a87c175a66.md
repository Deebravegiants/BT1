### Title
Fee-on-transfer/deflationary token accounting mismatch in Tron `IntentGatewayV2.placeOrder` leads to under-collateralized escrow - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The Tron variant of `IntentGatewayV2.placeOrder` computes escrowed amounts from the caller-supplied `order.inputs[i].amount` (minus protocol fee) instead of the amount the contract actually receives after `safeTransferFrom`. For fee-on-transfer/deflationary ERC20 input tokens, this creates an escrow record that promises more tokens than the gateway actually holds for that commitment, leading to insolvency of the escrow ledger. This is the exact bug class described in the external report (UserManager/UToken crediting `amount` instead of actual received amount), but here it manifests in Hyperbridge's intent-escrow accounting.

### Finding Description
In `evm/tron/contracts/apps/IntentGatewayV2.sol`, `placeOrder` computes `reducedInputs` (the amount that will be credited to escrow) directly from `order.inputs[i].amount` and the protocol fee *before* any token transfer occurs: [1](#0-0) 

Then, in the escrow phase, it performs the transfer and blindly credits `_orders[commitment][token]` with `reducedInputs[i].amount` regardless of what the contract actually received from `safeTransferFrom`: [2](#0-1) 

If the input token charges a transfer fee (fee-on-transfer/deflationary token), `IERC20(token).safeTransferFrom(msg.sender, address(this), order.inputs[i].amount)` delivers less than `order.inputs[i].amount` to the gateway, but `_orders[commitment][token]` is still credited with the full `reducedInputs[i].amount` (computed from the pre-fee, user-supplied amount). The commitment hash is also computed from the unreduced, un-adjusted `order.inputs`, so the discrepancy is baked into the on-chain escrow bookkeeping permanently.

This is precisely the bug class flagged in the report for `UserManager.stake`/`UToken._repayBorrowFresh`: the contract uses the nominal `amount` argument rather than the actually-received balance delta when crediting internal accounting for a fee-on-transfer token.

Notably, the main EVM contract `evm/src/apps/IntentGatewayV2.sol` was hardened against exactly this issue — it snapshots `balanceOf(address(this))` before and after each transfer and mutates `order.inputs[i].amount` to the actual received amount before computing the commitment and crediting escrow: [3](#0-2) 

The corresponding fee-on-transfer regression tests exist for the main EVM contract (`testPlaceOrder_FeeOnTransferToken_EscrowMatchesReceived`, `testPlaceOrder_FeeOnTransferToken_WithProtocolFee`, `testPlaceAndFill_FeeOnTransferToken_RoundTrip`, `testPlaceOrder_FeeOnTransferToken_Predispatch`): [4](#0-3) 

However, this fix and corresponding test coverage were not ported to the Tron deployment at `evm/tron/contracts/apps/IntentGatewayV2.sol`, which still uses the pre-fix pattern of crediting the nominal amount without a balance-delta check.

### Impact Explanation
When a fee-on-transfer token is used as an order input on the Tron deployment, the escrow ledger `_orders[commitment][token]` will record more tokens than the gateway actually holds for that order. Downstream consumers of this escrow — `fillOrder`/solver payout and the cross-chain `RedeemEscrow`/`RefundEscrow` handling — will attempt to pay out the over-stated `reducedInputs[i].amount`. Depending on the gateway's aggregate token balance across all outstanding orders:
- If the gateway's total balance for that token is insufficient, the payout transaction reverts, permanently freezing the user's escrowed funds (denial of service on withdrawal/fill).
- If the gateway holds balance from other unrelated orders in the same token (a very likely scenario since this is a shared pool contract), the shortfall is silently paid out of other users' escrowed tokens, i.e., theft/loss of funds for other order owners once enough such fee-on-transfer orders accumulate.

This satisfies "concrete theft or permanent freezing of funds" from an unprivileged, single-transaction path (`placeOrder` called by any user with a fee-on-transfer token as input).

### Likelihood Explanation
Likelihood is High: any user can call `placeOrder` with an arbitrary ERC20 as an input token (there is no allowlist/decimal/fee-behavior check visible in the reachable code), so an attacker or even an unaware user simply choosing a fee-on-transfer or rebasing/deflationary token as input triggers the mismatch on every such order. No privileged role or special conditions are required — a single transaction is sufficient to create an under-collateralized escrow entry.

### Recommendation
Port the balance-snapshot pattern already used in `evm/src/apps/IntentGatewayV2.sol` (lines 312-329) to the Tron contract: measure `balanceOf(address(this))` immediately before and after each `safeTransferFrom` for `order.inputs[i]`, and use the actual received delta (not the nominal `order.inputs[i].amount`) as the basis for computing `reducedInputs`, the commitment hash, and the amount credited to `_orders[commitment][token]`. Add fee-on-transfer regression tests mirroring `testPlaceOrder_FeeOnTransferToken_EscrowMatchesReceived` for the Tron gateway.

### Proof of Concept
1. Deploy a fee-on-transfer ERC20 (e.g., 1% fee, `FeeOnTransferToken` as used in `IntentGatewayV2SameChainTest.sol`) and mint tokens to `user`.
2. `user` approves the Tron `IntentGatewayV2` for `inputAmount = 1000e18` and calls `placeOrder` with this token as `order.inputs[0]`, `protocolFeeBps = 0` for simplicity.
3. In `placeOrder` (tron variant): `reducedInputs[0].amount = order.inputs[0].amount = 1000e18` (no protocol fee reduction here since `protocolFeeBps == 0`) — computed at lines 356-385 before any transfer occurs.
4. In the escrow phase (lines 450-469), `safeTransferFrom(user, address(this), 1000e18)` is called, but due to the 1% fee only `990e18` actually lands in the gateway (`fot.balanceOf(gateway) == 990e18`).
5. `_orders[commitment][token] += reducedInputs[0].amount` credits `1000e18`, even though the gateway only holds `990e18` of that token.
6. When a solver later calls `fillOrder`/redeems escrow for `1000e18`, the transfer either reverts (freezing funds) if the gateway has no surplus of that token from elsewhere, or succeeds by drawing down `10e18` from other users' escrowed balances of the same token, corrupting the shared accounting.

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
