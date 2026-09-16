### Title
Fee-on-transfer tokens cause escrow over-crediting and fund freezing in Tron IntentGatewayV2 - ([File: evm/tron/contracts/apps/IntentGatewayV2.sol])

### Summary
The Tron variant of `IntentGatewayV2.placeOrder` credits the escrow ledger (`_orders`) with the user-requested input amount (minus protocol fee), but never checks the actual token balance the contract received via `safeTransferFrom`. For fee-on-transfer ERC-20 tokens, the contract's recorded escrow balance exceeds its actual token holdings, causing later legitimate withdrawals (fills/cancels/refunds) to revert or drain funds meant for other users.

### Finding Description
In `placeOrder`, non-native inputs are pulled with a plain `safeTransferFrom` call and the escrow mapping is incremented by the pre-computed `reducedInputs[i].amount` — the amount the *user specified* (adjusted only for protocol fee), not the amount the *gateway actually received*: [1](#0-0) 

This is functionally identical to the PoolTogether `TwabRewards` bug pattern: reward/escrow accounting is derived from a nominal transfer amount rather than the measured post-transfer balance, so fee-on-transfer tokens silently create a shortfall between the ledger (`_orders[commitment][token]`) and the contract's real balance.

The same flaw exists in the `predispatch` branch, where dust/received amounts from the call-dispatcher sweep are computed against `requiredAmount`, but the final escrow credit still uses `reducedInputs[i].amount` rather than the measured `balance` actually swept back: [2](#0-1) 

Crucially, this bug was already identified and fixed in the canonical EVM contract, which measures `balanceOf` before and after each `safeTransferFrom`/sweep and mutates `order.inputs[i].amount` (and therefore the commitment and escrow credit) to the *actually received* amount: [3](#0-2) 

The dedicated fee-on-transfer regression tests confirm this is a recognized, intentionally-mitigated bug class for the main EVM contract: [4](#0-3) 

The Tron contract's `withdraw` function then pays out exactly `body.tokens[i].amount` (the nominal, un-adjusted amount) via a raw `token.call` and only decrements `_orders[commitment][token]` after the transfer, with no balance-sufficiency check before the transfer: [5](#0-4) 

Because `_orders[commitment][token]` was credited with more than the contract actually holds for that token, and withdrawals pay out based on that inflated ledger value, the contract can attempt to transfer more tokens than it possesses. Fee-on-transfer tokens are not enumerated/blocked anywhere in the Tron contract.

### Impact Explanation
This is a real fund-freezing/fund-loss vulnerability reachable by any unprivileged user submitting `placeOrder` with a fee-on-transfer ERC-20 as an input token:
- If multiple orders share the same fee-on-transfer token, the pooled contract balance for that token becomes insufficient relative to the sum of all `_orders[...][token]` entries.
- Whichever solver/user withdraws first (via `fillOrder`→`withdraw`, `cancelOrder`, or `RedeemEscrow`/`RefundEscrow` cross-chain callbacks) can drain more than their fair share, or, once the shortfall accumulates, subsequent legitimate withdrawals will revert (`TransferFailed`) — permanently freezing those users' escrowed funds, since there's no recovery path other than an admin-only `SweepDust` request that requires a Hyperbridge-authorized cross-chain message.
- This satisfies the "concrete theft or permanent freezing of funds" bar from an ordinary user-triggered path (placing/filling/cancelling an intent order).

### Likelihood Explanation
Likelihood is High: no privileged role is required, and the attacker/trigger is simply any user who places (or is caused to have placed on their behalf, e.g. via a malicious/careless integration) an order denominated in a fee-on-transfer token — a well-known real-world token category (e.g. deflationary/tax tokens). The bug is deterministic, not probabilistic, and triggers on the very first `placeOrder` call using such a token.

### Recommendation
Mirror the fix already present in `evm/src/apps/IntentGatewayV2.sol`: measure `IERC20(token).balanceOf(address(this))` immediately before and after each `safeTransferFrom`/sweep call in the Tron contract's `placeOrder`, and use the delta (actual received amount) — not the nominal requested amount — both when computing `reducedInputs`/the commitment hash and when crediting `_orders[commitment][token]`. Apply the same measured-delta approach to the `predispatch` sweep path.

### Proof of Concept
1. Deploy a 1%-fee ERC-20 token (as in `FeeOnTransferToken` from the test suite) and mint balance to `user`.
2. `user` approves the Tron `IntentGatewayV2` for `inputAmount = 1000e18` and calls `placeOrder` with that token as an input, `protocolFeeBps = 0`.
3. `safeTransferFrom(msg.sender, address(this), 1000e18)` actually delivers only `990e18` to the gateway (1% fee burned), confirmed by the pattern already tested for the main EVM contract in `testPlaceOrder_FeeOnTransferToken_EscrowMatchesReceived`.
4. However, unlike the main EVM contract, the Tron contract's `_orders[commitment][token]` is credited with the full `reducedInputs[i].amount = 1000e18` (protocol fee is 0), not the actually-received `990e18`.
5. A second, unrelated order using the same token is placed and similarly over-credited.
6. When the first order is filled/withdrawn via `withdraw()`, the contract attempts to `token.call(transfer, beneficiary, 1000e18)` while it may hold less than that combined with the second order's obligations — either this specific transfer succeeds by cannibalizing the second order's escrowed balance, or a later withdrawal for the second order reverts with `TransferFailed` because the token balance is insufficient, permanently freezing that user's funds. [6](#0-5) [7](#0-6)

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
