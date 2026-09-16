Confirmed: the tron variant's `placeOrder` (non-predispatch path) performs `IERC20(token).safeTransferFrom(msg.sender, address(this), order.inputs[i].amount)` without checking actual received balance, then credits `_orders[commitment][token] += reducedInputs[i].amount` which is derived only from the original requested amount minus protocol fee — not from the actual tokens received. This is the exact analog of the Cooler fee-on-transfer bug, and it's already fixed in the sibling `evm/src/apps/IntentGatewayV2.sol` implementation (which measures `balanceOf` before/after and mutates `order.inputs[i].amount` to the actual received amount) but the fix was not applied to `evm/tron/contracts/apps/IntentGatewayV2.sol`.

### Title
IntentGatewayV2 (Tron) escrows fee-on-transfer token amounts using requested amount instead of actual received amount, causing escrow over-crediting and fund insolvency - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
`placeOrder` in the Tron IntentGatewayV2 contract credits escrow (`_orders[commitment][token]`) based on `reducedInputs[i].amount`, which is derived solely from `order.inputs[i].amount` (the user-specified amount) minus the protocol fee. It never measures the gateway's actual token balance received via `safeTransferFrom`. For any ERC20 token that charges a transfer fee (fee-on-transfer / deflationary tokens), the contract will record more escrowed tokens than it actually holds.

### Finding Description
In the non-predispatch escrow branch: [1](#0-0) 
the code calls `IERC20(token).safeTransferFrom(msg.sender, address(this), order.inputs[i].amount)` and then unconditionally credits `_orders[commitment][token] += reducedInputs[i].amount`, where `reducedInputs[i].amount` is computed purely from `order.inputs[i].amount` reduced by the protocol fee basis points: [2](#0-1) 
No `balanceOf(address(this))` check before/after transfer exists to account for tokens that deduct a fee on transfer. The predispatch branch has a partial `balanceOf(dispatcher)` sufficiency check but still stores `reducedInputs[i].amount` (based on the pre-transfer requested amount) into escrow rather than the amount actually swept back to the gateway: [3](#0-2) 

By contrast, the EVM mainline implementation explicitly guards against this by measuring `balanceOf` before and after the transfer and mutating `order.inputs[i].amount` to the actual received amount before computing the commitment/escrow: [4](#0-3) 
This defensive logic — confirmed by the fee-on-transfer test suite (`testPlaceOrder_FeeOnTransferToken_EscrowMatchesReceived`, etc.) — is entirely absent from the Tron contract: [5](#0-4) 

### Impact Explanation
Any deflationary/fee-on-transfer ERC20 token used as an order input on the Tron deployment causes the gateway to record escrow balances exceeding its true token holdings. Once several such orders accumulate, the sum of all `_orders[...][token]` claims exceeds the contract's actual balance of that token. When solvers fill orders and redeem escrow (`_withdraw`/`RedeemEscrow`), or when users cancel and reclaim escrow, later claimants will find the contract under-funded, causing reverts (denial of service / permanent freezing of funds for some legitimate claimants) or, if redemption order allows it, earlier claimants to drain funds meant for others — a direct fund-accounting/insolvency vulnerability reachable by any unprivileged user simply calling `placeOrder` with a fee-on-transfer token.

### Likelihood Explanation
Triggering this requires only that the Tron IntentGatewayV2 allow (i.e., not explicitly disallow) a fee-on-transfer token as an input asset. Since there is no token-fee detection/allowlist restricting inputs in `placeOrder`, any user can submit an order with such a token in a single, ordinary transaction to create the escrow/balance mismatch — no privileged role or special conditions needed.

### Recommendation
Mirror the mitigation already present in `evm/src/apps/IntentGatewayV2.sol`: measure `IERC20(token).balanceOf(address(this))` (or `balanceOf(dispatcher)` for the predispatch branch) immediately before and after each `safeTransferFrom`/sweep, and use the actual delta (not the user-requested `order.inputs[i].amount`) as the basis for computing `reducedInputs`, the commitment hash, and the escrow credit in `evm/tron/contracts/apps/IntentGatewayV2.sol`.

### Proof of Concept
1. Deploy a 1% fee-on-transfer ERC20 token (as in `FeeOnTransferToken` from the test suite) and register it as `_underlying`/order-input token on the Tron `IntentGatewayV2`.
2. User calls `placeOrder` with `inputs[0] = {token: FOT, amount: 1000e18}` and `protocolFeeBps = 0` for simplicity.
3. `safeTransferFrom(msg.sender, address(this), 1000e18)` executes; due to the 1% fee, the gateway's actual FOT balance only increases by `990e18`.
4. Because `protocolFeeBps == 0`, `reducedInputs[0].amount = order.inputs[0].amount = 1000e18` (unreduced), so `_orders[commitment][FOT] = 1000e18`, even though the contract holds only `990e18`.
5. When the order is filled/redeemed and `_withdraw` attempts to pay out `1000e18` of FOT from escrow, the contract's real balance (`990e18`, minus whatever additional transfer fee applies on the outgoing leg) is insufficient — causing either a revert (locked funds for legitimate parties) or, in a multi-order scenario, insolvency where later escrow claims cannot be honored due to shared balance depletion by earlier fee-inflated claims.

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
