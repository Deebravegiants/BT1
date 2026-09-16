### Title
Fee-on-transfer token accounting mismatch in Tron `IntentGatewayV2.placeOrder` causes escrow insolvency and fund loss/DoS on redemption - (File: evm/tron/contracts/apps/IntentGatewayV2.sol)

### Summary
The Tron fork of `IntentGatewayV2.placeOrder` credits the internal escrow ledger `_orders[commitment][token]` with the *declared/reduced* input amount rather than the amount actually received by the contract via `IERC20.transferFrom`. For fee-on-transfer (or otherwise deflationary) ERC-20 tokens, this causes the escrow accounting to overstate the tokens actually held by the gateway, mirroring the Carapace `ProtectionPool._deposit` bug where minted sToken/`totalSTokenUnderlying` didn't account for transfer fees.

### Finding Description
In `placeOrder`, for the non-predispatch path the contract does: [1](#0-0) 

`IERC20(token).safeTransferFrom(msg.sender, address(this), order.inputs[i].amount)` is called, but the actual balance delta is never measured. Immediately after, `_orders[commitment][token] += reducedInputs[i].amount;` credits the escrow with the *requested* amount (minus protocol fee if any), not what the contract actually received.

The same pattern repeats in the predispatch branch, where dust is computed from `balance - requiredAmount` (the *dispatcher's* balance vs the declared required amount, not what the gateway itself received after the second transfer), and then again `_orders[commitment][token] += reducedInputs[i].amount;` is credited with the declared reduced amount: [2](#0-1) 

By contrast, the canonical (non-Tron) `evm/src/apps/IntentGatewayV2.sol` was hardened against exactly this class of bug: it snapshots `balanceOf` before and after every transfer and mutates `order.inputs[i].amount` to the actual received amount before computing the commitment/escrow: [3](#0-2) 

The dedicated test suite `IntentGatewayV2SameChainTest.sol` even encodes this fix as an explicit invariant ("Escrow should equal actual received amount," "Escrow should equal received minus protocol fee"): [4](#0-3) 

The Tron variant, however, still uses the unfixed pattern — it computes `reducedInputs` purely from the user-declared `order.inputs[i].amount` and protocol fee percentage, and never reconciles against the gateway's real token balance: [5](#0-4) 

### Impact Explanation
Because `_orders[commitment][token]` (the escrow ledger used for solver reimbursement/redemption via `RedeemEscrow` and for order cancellation refunds) is credited with more tokens than the gateway actually holds for fee-on-transfer tokens, the pool of that token becomes globally under-collateralized. Since `_orders` entries for different commitments/orders share the same physical token balance of the contract, this creates a race: whichever order is filled/redeemed/cancelled last for that token will find insufficient actual balance, causing `safeTransfer`/`transferFrom` to revert (denial of service, escrowed funds get stuck) or, if a fee-on-transfer token also applies a fee during the outbound transfer, the recipient receives less than their properly-accounted escrow, and downstream users lose funds because the shortfall compounds across orders. This is a direct token-bridge/intents-escrow accounting bug reachable by any unprivileged user submitting `placeOrder` with a fee-on-transfer ERC20 as input.

### Likelihood Explanation
Any user can supply an arbitrary ERC20 token address as an order input; the `IntentGatewayV2` contract does not restrict tokens to a fee-free allowlist. Placing a single `placeOrder` call with a fee-on-transfer token is sufficient to trigger the mismatch — no privileged role or complex multi-step exploit needed, and the existing test-suite already demonstrates the exact failure mode is understood and fixed elsewhere in the codebase but left unpatched in the Tron variant, indicating a straightforward regression/fork-sync bug.

### Recommendation
Apply the same fix used in `evm/src/apps/IntentGatewayV2.sol` to `evm/tron/contracts/apps/IntentGatewayV2.sol`: snapshot the contract's token balance immediately before and after each `safeTransferFrom` call, compute `received = balanceAfter - balanceBefore`, and use `received` (further reduced by protocol fee) both when computing the order commitment and when incrementing `_orders[commitment][token]`, ensuring escrow accounting always matches actual custody of funds.

### Proof of Concept
1. Deploy a fee-on-transfer ERC20 token (e.g., 1% fee, as modeled by `FeeOnTransferToken` in `IntentGatewayV2SameChainTest.sol`) and mint balance to a user.
2. User calls `placeOrder` on the Tron `IntentGatewayV2` with `order.inputs[0] = {token: FOT, amount: 1000e18}` and no protocol fee.
3. `safeTransferFrom(user, address(this), 1000e18)` executes; due to the 1% fee, the gateway's actual `balanceOf(this)` only increases by `990e18`.
4. `_orders[commitment][FOT] += reducedInputs[0].amount` credits `1000e18` (since `reducedInputs == order.inputs` when no protocol fee is set) — a `10e18` overstatement versus actual contract balance.
5. Repeat with another user/order using the same FOT token. The cumulative escrow ledger across orders now exceeds actual `balanceOf(gateway)` by the sum of all transfer fees.
6. When solvers attempt to redeem escrow via the `RedeemEscrow` request path for the last order(s) sharing this token, the `transfer`/`safeTransfer` calls will revert due to insufficient actual balance, freezing that order's funds, or earlier redemptions silently "borrow" from the shortfall meant for later legitimate claimants.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L338-385)
```text
    function placeOrder(Order memory order, bytes32 graffiti) public payable {
        // Validate that order has inputs
        if (order.inputs.length == 0) revert InvalidInput();

        address hostAddr = host();
        // fill out the order preludes
        order.user = bytes32(uint256(uint160(msg.sender)));
        order.source = IDispatcher(hostAddr).host();
        order.nonce = _nonce++;

        // Calculate reduced inputs (after protocol fees) for commitment and escrow
        uint256 inputsLen = order.inputs.length;
        // Use destination-specific protocol fee, fallback to source chain fee if zero
        bytes32 destinationHash = keccak256(order.destination);
        uint256 protocolFeeBps = _destinationProtocolFees[destinationHash];
        if (protocolFeeBps == 0) {
            protocolFeeBps = _params.protocolFeeBps;
        }
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
