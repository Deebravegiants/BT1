Confirmed. The Tron deployment of `IntentGatewayV2.sol` diverges from the EVM version's fee-on-transfer fix. In `placeOrder`'s non-predispatch branch, the token is pulled via `IERC20(token).safeTransferFrom(msg.sender, address(this), order.inputs[i].amount)` with no post-transfer balance check, yet the escrow ledger `_orders[commitment][token]` is credited with `reducedInputs[i].amount` (the requested amount only reduced by the protocol fee), not the amount actually received by the contract.

### Title
Fee-on-Transfer Tokens Cause Escrow Over-Crediting and Insolvency in Tron IntentGatewayV2 - (File: evm/tron/contracts/apps/IntentGatewayV2.sol)

### Summary
The Tron variant of `IntentGatewayV2.placeOrder` credits the internal escrow accounting (`_orders[commitment][token]`) with the user-declared input amount (minus only the protocol fee), instead of the amount actually received by the contract after `safeTransferFrom`. For any ERC20 with a transfer fee/tax, the contract will record more escrowed tokens than it actually holds.

### Finding Description
In the standard (non-predispatch) escrow path: [1](#0-0) 
the contract does `IERC20(token).safeTransferFrom(msg.sender, address(this), order.inputs[i].amount)` and then unconditionally does `_orders[commitment][token] += reducedInputs[i].amount;`, where `reducedInputs[i].amount` is `originalAmount - protocolFee` computed purely from the user-supplied `order.inputs[i].amount`: [2](#0-1) 

If `token` charges a transfer fee (fee-on-transfer / deflationary token), the actual balance increase on the gateway is less than `order.inputs[i].amount`, but the escrow ledger is credited as though the full (protocol-fee-adjusted) amount arrived. The predispatch path has a partial safeguard — it measures the dispatcher's actual balance before sweeping — but even there the transfer from `dispatcher` back to the gateway itself is not balance-checked before crediting `reducedInputs[i].amount`: [3](#0-2) 

By contrast, the current EVM `IntentGatewayV2.sol` (non-Tron) was hardened against exactly this class of bug — it measures `balanceOf` deltas before and after each transfer and mutates `order.inputs[i].amount` to the actual amount received: [4](#0-3) 
This fix was not ported to the Tron contract, and there are dedicated fee-on-transfer regression tests for the EVM contract but none for the Tron one: [5](#0-4) 

The withdrawal path (`withdraw`) then pays out escrowed amounts by trusting the ledger, decrementing `_orders[body.commitment][token] -= amount` and transferring `amount` to the beneficiary: [6](#0-5) 
Because the ledger for a fee-on-transfer input token is inflated beyond the gateway's real balance, the sum of all outstanding escrow claims across orders can exceed the actual token balance held by the contract.

### Impact Explanation
This is a fund-freezing/insolvency bug reachable by any unprivileged user calling `placeOrder` with a fee-on-transfer or deflationary ERC20 as an input asset. Once even one such order is placed, the internal accounting for that token becomes permanently overstated relative to the real balance. Subsequent solvers who correctly fill earlier (non-fee) orders for the same token can find the contract unable to pay out the full escrowed amount, and/or a solver who fills the fee-token order can be told they're entitled to more tokens than the contract actually has — resulting in either a revert (temporary freezing) for the last claimant needing withdrawal, or if the token allows self-referential griefing, silently draining tokens rightfully owed to other users' escrows once the contract's balance is depleted below the sum of claims (fund loss for other users sharing that same asset's escrow pool). This meets the "permanent freezing/loss of funds" bar because there is no accounted mechanism to true-up the ledger to real balances (no dust-emission or received-amount check exists on this path, unlike the sibling EVM contract).

### Likelihood Explanation
Likelihood is limited to intent-gateway deployments that support fee-on-transfer/deflationary tokens as tradeable input assets on Tron (which has its own token ecosystem including such tax tokens); any single unprivileged `placeOrder` call with such a token as input triggers the miscrediting, so exploitation requires no privileged access and no colluding solver — just choosing a fee-charging token as the order's input asset.

### Recommendation
Mirror the fix already present in `evm/src/apps/IntentGatewayV2.sol`: measure the contract's (and, for predispatch, the dispatcher's) actual token balance before and after each `safeTransferFrom`/sweep, and credit `_orders[commitment][token]` with the delta actually received (after subtracting protocol fee proportionally on the received amount) rather than with the caller-declared `order.inputs[i].amount`. Alternatively, explicitly reject input tokens whose received amount doesn't match the requested amount.

### Proof of Concept
1. Deploy the Tron `IntentGatewayV2` and a fee-on-transfer ERC20 `FOT` (e.g. 1% fee per transfer), analogous to the `FeeOnTransferToken` test helper already used for the EVM contract's regression tests.
2. User calls `placeOrder` with `order.inputs[0] = {token: FOT, amount: 1000e18}`, `protocolFeeBps = 0` for simplicity.
3. `safeTransferFrom(user, gateway, 1000e18)` executes; gateway's actual `FOT` balance increases by only `990e18` (1% fee retained/burned by the token contract).
4. Contract nonetheless executes `_orders[commitment][FOT] += reducedInputs[0].amount` = `1000e18` (since `reducedInputs == order.inputs` when no protocol fee).
5. Gateway's ledger now claims `1000e18` of `FOT` escrowed for this order, but it physically holds only `990e18`.
6. When a solver fills the order and `withdraw()` is invoked, `_orders[commitment][FOT] -= 1000e18` and `token.call(transfer(beneficiary, 1000e18))` is attempted — this either reverts (DoS/freezing of the solver's payout) or, if other unrelated escrowed `FOT` balances from other orders are commingled in the contract's single token balance, succeeds by consuming `10e18` that belongs to other orders' escrow, corrupting the ledger for those orders too.

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

**File:** evm/src/apps/IntentGatewayV2.sol (L313-328)
```text
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
