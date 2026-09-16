### Title
`IntentGatewayV2.placeOrder()` (Tron) escrows the full nominal input amount instead of the amount actually received, causing insolvent/inflated escrow accounting for fee-on-transfer ERC20 tokens - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The Tron fork of `IntentGatewayV2.placeOrder()` records escrowed balances in `_orders[commitment][token]` based on the order's declared `inputs[i].amount` (reduced only by the protocol fee), without ever measuring the actual token balance the contract received via `balanceOf` diffing. For fee-on-transfer ERC20 input tokens this diverges from the EVM version of the same contract, which explicitly guards against this class of bug.

### Finding Description
In the no-predispatch path of `placeOrder()`: [1](#0-0) 

the contract does `IERC20(token).safeTransferFrom(msg.sender, address(this), order.inputs[i].amount)` and then unconditionally credits `_orders[commitment][token] += reducedInputs[i].amount`, where `reducedInputs[i].amount` is derived purely from the user-supplied `order.inputs[i].amount` minus the protocol fee percentage: [2](#0-1) 

If `token` is a fee-on-transfer ERC20, `safeTransferFrom` delivers strictly less than `order.inputs[i].amount` to the contract, yet the escrow ledger is credited as if the full nominal amount arrived. The predispatch path has the same defect: it computes `dust = balance - requiredAmount` from the dispatcher's balance and credits `reducedInputs[i].amount` to escrow, but never checks the actual balance received by `address(this)` after the `IERC20.transfer` sweep call, which itself can incur a second transfer fee: [3](#0-2) 

This is the direct structural analog of the reported bug class: `doPutCollateral()` assumed `werc20.mint()`'s return value equals the transferred `amount`, ignoring fee-on-transfer effects and creating an accounting entry not backed by actual tokens held. Here, the Tron `IntentGatewayV2` assumes the escrowed/committed amount equals the nominal input amount, ignoring the fee-on-transfer effect on `safeTransferFrom`/`transfer`, creating an escrow ledger entry that overstates the tokens actually custodied by the contract.

Notably, the sibling EVM implementation (`evm/src/apps/IntentGatewayV2.sol`) was hardened against exactly this scenario by snapshotting `balancesBefore`/`balancesAfter` and mutating `order.inputs[i].amount` to the actual received amount before computing fees and escrow: [4](#0-3) 

The Tron variant lacks this balance-diff logic entirely, indicating the fix was not ported.

### Impact Explanation
The escrow accounting (`_orders[commitment][token]`) becomes inflated relative to the token balance actually held by the `IntentGatewayV2` contract on Tron. Because escrow entries for different orders/tokens are aggregated in the same contract-wide token balance, this shortfall means either:
- A legitimate `fillOrder`/refund/withdrawal against this order's escrow can partially draw down tokens that were actually escrowed for *other* orders (fund misallocation across users), or
- Once the shortfall is discovered, downstream transfers relying on the escrowed amount can revert due to insufficient actual balance, permanently freezing the order's (and potentially other users') funds, mirroring the `bank.putCollateral()` revert in the original report.

This satisfies "concrete theft or permanent freezing of funds" for a path reachable by any unprivileged user placing an order with a fee-on-transfer input token.

### Likelihood Explanation
Likelihood is contingent on fee-on-transfer or deflationary ERC20 tokens being accepted as `order.inputs` tokens on the Tron deployment. If the gateway's input token allow-list is unrestricted (as appears to be the case — any ERC20 address can be encoded in `TokenInfo.token`), any user can trigger this by placing an order with such a token, requiring no special privileges.

### Recommendation
Port the balance-before/after measurement pattern from `evm/src/apps/IntentGatewayV2.sol` (lines 291–328) into `evm/tron/contracts/apps/IntentGatewayV2.sol`: after each `safeTransferFrom`/predispatch sweep, compute the actual amount received via `balanceOf` diffing, mutate `order.inputs[i].amount` (and thus `reducedInputs[i].amount`/the commitment) to the real received value, and only escrow that real amount in `_orders[commitment][token]`.

### Proof of Concept
1. Deploy a 1% fee-on-transfer ERC20 token and register it as an input asset.
2. User calls `placeOrder()` with `order.inputs[0] = {token: FOT, amount: 1000e18}` and no predispatch.
3. `safeTransferFrom(msg.sender, address(this), 1000e18)` delivers only 990e18 to the gateway (`fot.balanceOf(gateway) == 990e18`).
4. `_orders[commitment][FOT]` is credited with `reducedInputs[0].amount`, computed from the full `1000e18` (minus only the protocol fee), i.e. ~997e18 (with 30bps protocol fee) — more than the 990e18 actually held.
5. When a solver or refund flow later attempts to move `_orders[commitment][FOT]` (~997e18) out of the contract, it either reverts due to insufficient token balance (freezing) or succeeds by drawing on tokens escrowed for other unrelated orders (fund misallocation/theft), exactly mirroring the `doPutCollateral()`/`bank.putCollateral()` revert-and-insolvency pattern in the original report. This is directly confirmed by the equivalent Foundry test suite for the fixed EVM contract, which explicitly validates that escrow must equal actual received amount for fee-on-transfer tokens: [5](#0-4)  — a test/guard absent from the Tron variant.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L356-385)
```text
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

**File:** evm/src/apps/IntentGatewayV2.sol (L291-328)
```text
            // Measure actual received, emit dust for excess, update order.inputs.
            for (uint256 i; i < inputsLen;) {
                address token = address(uint160(uint256(order.inputs[i].token)));
                uint256 received;
                if (token == address(0)) {
                    received = address(this).balance - balancesBefore[i];
                } else {
                    received = IERC20(token).balanceOf(address(this)) - balancesBefore[i];
                }

                if (received > order.inputs[i].amount) {
                    uint256 dust = received - order.inputs[i].amount;
                    emit DustCollected(token, dust);
                } else {
                    order.inputs[i].amount = received;
                }

                unchecked {
                    ++i;
                }
            }
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
