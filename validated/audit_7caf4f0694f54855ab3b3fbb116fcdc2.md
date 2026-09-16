## Finding

Fee-on-transfer tokens desynchronize escrow accounting from actual token balance in the Tron variant of `IntentGatewayV2`, unlike the canonical EVM implementation which was hardened against exactly this class of bug.

### Title
Fee-on-transfer tokens break escrow accounting and withdrawal in Tron `IntentGatewayV2.placeOrder` - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The canonical EVM `IntentGatewayV2.placeOrder` measures the gateway's actual token balance before/after `safeTransferFrom` and uses the *received* amount to compute escrow credits and the order commitment, explicitly to defend against fee-on-transfer tokens [1](#0-0) , with the actual-balance-diff logic at [2](#0-1) , validated by dedicated fee-on-transfer tests [3](#0-2) .

The Tron port of the same contract, `evm/tron/contracts/apps/IntentGatewayV2.sol`, lacks this fix. Its `placeOrder` computes `reducedInputs`/escrow credit directly from the caller-supplied `order.inputs[i].amount` (minus protocol fee) — never checking the gateway's actual balance received from `safeTransferFrom`: [4](#0-3) 

### Finding Description
In the non-predispatch branch, the contract calls `IERC20(token).safeTransferFrom(msg.sender, address(this), order.inputs[i].amount)` and then immediately credits `_orders[commitment][token] += reducedInputs[i].amount` — where `reducedInputs[i].amount` is derived purely from the nominal `order.inputs[i].amount` supplied by the user, reduced only by the protocol fee bps [5](#0-4) [4](#0-3) .

If the input token charges a transfer fee, the gateway's actual received balance is strictly less than `order.inputs[i].amount`, but the escrow ledger `_orders[commitment][token]` is credited with the full (pre-fee) reduced amount. This is the identical root cause as the referenced Teller report: stored accounting (`collateralInfo._amount` / here `_orders[...]`) diverges from actual on-chain balance for fee-on-transfer tokens.

Because `_orders` is a per-commitment ledger drawn against a single shared token balance held by the contract, this over-crediting is not confined to the affected order — it can make the contract's aggregate liabilities exceed its actual token balance. The predispatch branch of the same function similarly measures `balance = IERC20(token).balanceOf(dispatcher)` only to check sufficiency for the *sweep*, but still credits escrow with `reducedInputs[i].amount` computed from the nominal `order.inputs[i].amount`, not the amount actually swept back to the gateway [6](#0-5) .

### Impact Explanation
When the escrow is later released — via `withdraw`/`onAccept` processing `RedeemEscrow`/`RefundEscrow` [7](#0-6)  — the contract will attempt to transfer out the inflated `_orders[commitment][token]` amount. Since the actual token balance is short by the transfer-fee amount, either:
- The withdrawal transaction reverts (insufficient balance), permanently freezing that order's collateral (denial of withdrawal/liquidation, matching the referenced report's impact), or
- Because the shortfall is drawn from a shared token balance across all orders, satisfying this order's inflated withdrawal can consume tokens that rightfully belong to other users' unrelated escrowed orders, causing later legitimate withdrawals for other commitments to fail — an insolvency/fund-freezing condition across the pool, not just the single affected order.

This satisfies "permanent freezing of funds" / unsound accounting for a route that is unable to deliver committed funds.

### Likelihood Explanation
Any user can place an order using a fee-on-transfer ERC-20 as input on Tron; no privileged role is required. The Tron `IntentGatewayV2` is a production, unprivileged-facing contract identical in purpose to the already-patched EVM version, indicating this is a known bug class in this codebase that was fixed on one chain but left unpatched on Tron.

### Recommendation
Apply the same balance-before/after fix used in `evm/src/apps/IntentGatewayV2.sol` to `evm/tron/contracts/apps/IntentGatewayV2.sol`: snapshot `IERC20(token).balanceOf(address(this))` (or `dispatcher`, for the predispatch sweep case) before each `safeTransferFrom`/sweep, and use the actual delta to (a) mutate `order.inputs[i].amount`, (b) compute the protocol-fee-reduced amount, and (c) credit `_orders[commitment][token]`, exactly mirroring `evm/src/apps/IntentGatewayV2.sol` lines 230–329.

### Proof of Concept
1. Deploy `IntentGatewayV2` (Tron variant) with `protocolFeeBps = 0` for simplicity.
2. Deploy a fee-on-transfer ERC-20 with e.g. 1% fee, mint 1000 tokens to `user`.
3. `user` approves the gateway for 1000 tokens and calls `placeOrder` with `order.inputs[0].amount = 1000e18`.
4. Inside `placeOrder`, `safeTransferFrom(user, address(this), 1000e18)` results in the gateway actually receiving only 990e18 (1% fee retained), per [8](#0-7) .
5. `_orders[commitment][token]` is nonetheless credited with 1000e18 (no protocol fee reduction, so `reducedInputs[i].amount == order.inputs[i].amount == 1000e18`) per [9](#0-8) , while `IERC20(token).balanceOf(address(this)) == 990e18`.
6. When `RedeemEscrow`/`RefundEscrow` withdrawal for this commitment attempts to transfer 1000e18 to the beneficiary, it reverts due to insufficient balance — the order's collateral is permanently stuck, and if any of the shortfall is masked by other orders' escrowed balance, subsequent legitimate withdrawals for unrelated commitments can also fail.

### Citations

**File:** evm/src/apps/IntentGatewayV2.sol (L230-234)
```text
        // Phase 1: Transfer tokens and record actual received amounts.
        // For fee-on-transfer tokens, the gateway receives less than the requested amount.
        // We mutate order.inputs to reflect actual received so the commitment and escrow
        // are consistent with what the gateway holds.
        uint256 msgValue = msg.value;
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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L451-469)
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
        }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L629-635)
```text
    function onAccept(IncomingPostRequest calldata incoming) external override onlyHost {
        RequestKind kind = RequestKind(uint8(incoming.request.body[0]));
        if (kind == RequestKind.RedeemEscrow || kind == RequestKind.RefundEscrow) {
            authenticate(incoming.request);
            WithdrawalRequest memory body = abi.decode(incoming.request.body[1:], (WithdrawalRequest));
            return withdraw(body, kind == RequestKind.RefundEscrow);
        }
```
