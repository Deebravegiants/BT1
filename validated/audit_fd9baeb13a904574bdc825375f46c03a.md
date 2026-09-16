### Title
Fee-on-transfer tokens inflate escrow accounting in `IntentGatewayV2.placeOrder` (Tron variant), decoupling `_orders[commitment][token]` from actual token balance held - (File: evm/tron/contracts/apps/IntentGatewayV2.sol)

### Summary
The Tron deployment of `IntentGatewayV2` computes the escrowed amount recorded in `_orders[commitment][token]` from the user-supplied `order.inputs[i].amount` (via `reducedInputs`) **before** any token transfer occurs, and never verifies how many tokens the contract actually received. For fee-on-transfer / deflationary ERC20s, the contract will record more escrow than it actually holds, exactly mirroring the reported Allo `poolAmount` bug class where accounting is driven by the nominal transfer amount instead of the actual balance delta.

### Finding Description
In `placeOrder` (evm/tron/contracts/apps/IntentGatewayV2.sol), the commitment and `reducedInputs` (the amount that gets credited to escrow) are derived directly from `order.inputs[i].amount`, prior to executing any transfer: [1](#0-0) 

The actual token transfer into the gateway (non-predispatch path) then blindly calls `safeTransferFrom` for the *requested* amount, with no balance-before/balance-after check, and credits escrow with the pre-computed `reducedInputs[i].amount`: [2](#0-1) 

The predispatch path has the same flaw: it sweeps `balance` from the dispatcher based on `IERC20(token).balanceOf(dispatcher)` but still credits escrow using `reducedInputs[i].amount`, which was computed from the pre-transfer requested amount rather than what the gateway actually received: [3](#0-2) 

This is a regression relative to the main EVM implementation, `evm/src/apps/IntentGatewayV2.sol`, which correctly measures actual received amounts via balance snapshots (`balBefore`/`balancesBefore`) **before** computing protocol fees and the commitment, and mutates `order.inputs[i].amount` to the real received value: [4](#0-3) [5](#0-4) 

This exact fee-on-transfer accounting discipline is also covered by dedicated tests for the main gateway (`testPlaceOrder_FeeOnTransferToken_EscrowMatchesReceived`, `testPlaceAndFill_FeeOnTransferToken_RoundTrip`, `testPlaceOrder_FeeOnTransferToken_Predispatch`), confirming the project is aware of and defends against this exact bug class elsewhere — but the Tron contract lacks the equivalent protection: [6](#0-5) [7](#0-6) 

### Impact Explanation
For any input token that charges a transfer fee, burns on transfer, or otherwise delivers less than the nominal `amount` (deflationary/rebasing ERC20s), the Tron `IntentGatewayV2` will record an escrow (`_orders[commitment][token]`) larger than the tokens it actually custodies. Since escrow accounting underpins solver payouts, refunds/cancellations, and cross-chain redemption of the escrowed funds, this creates an under-collateralized escrow ledger: the sum of all `_orders` entries for that token can exceed the gateway's real token balance. This can lead to later legitimate withdrawals (redeem/refund/cancel flows) reverting due to insufficient balance, or — if multiple orders interact with shared token liquidity — one order's inflated accounting effectively siphoning value that should back another user's order, resulting in loss of funds/inability to redeem for some order holders. This is a permanent freezing/loss-of-funds condition, not merely cosmetic.

### Likelihood Explanation
Any unprivileged user calling `placeOrder` with a fee-on-transfer, deflationary, or rebasing ERC20 as an input token triggers the flaw — no special privileges or governance/administrative access are required. The only precondition is that such a token is accepted as an order input, which the contract does not prevent (no allowlist rejecting fee-on-transfer tokens is visible in the reviewed code). This makes the likelihood high wherever the deployment permits arbitrary ERC20 inputs.

### Recommendation
Apply the same fix already present in `evm/src/apps/IntentGatewayV2.sol` to the Tron contract: measure the gateway's/dispatcher's token balance immediately before and after each `transferFrom`/sweep, use the actual received delta as `order.inputs[i].amount`, and compute `protocolFeeBps`, `reducedInputs`, and the commitment hash strictly from these actual-received amounts — not from the caller-supplied nominal `amount` — before crediting `_orders[commitment][token]`.

### Proof of Concept
1. Deploy `IntentGatewayV2` (Tron variant) and a fee-on-transfer ERC20 (e.g., 1% fee), matching the `FeeOnTransferToken` test helper already used against the main gateway: [8](#0-7) 
2. User calls `placeOrder` with `order.inputs[0] = {token: FOT, amount: 1000e18}` and no `protocolFeeBps` configured.
3. In the Tron contract, `reducedInputs[0].amount` (or `order.inputs[0].amount` when `protocolFeeBps == 0`) is fixed at `1000e18` before transfer (lines 348-385).
4. `safeTransferFrom(msg.sender, address(this), 1000e18)` executes; due to the 1% fee, the gateway only receives `990e18` tokens — this exactly parallels the reported PoC from the external report where the "MockStrategy" received `8900` fee tokens while `poolAmount` was credited `9000`.
5. `_orders[commitment][token] += reducedInputs[0].amount` credits `1000e18` into escrow, while `IERC20(token).balanceOf(address(this))` is only `990e18` — a `10e18` shortfall between recorded escrow and real balance, reproducing the same "escrow > actual balance" bug class as the Allo `poolAmount` report.

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

**File:** evm/src/apps/IntentGatewayV2.sol (L291-311)
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

**File:** evm/tests/foundry/IntentGatewayV2SameChainTest.sol (L2624-2686)
```text
    /// @notice Fee-on-transfer through the predispatch path: escrow reflects actual received.
    function testPlaceOrder_FeeOnTransferToken_Predispatch() public {
        FeeOnTransferToken fot = new FeeOnTransferToken(100); // 1% transfer fee
        fot.mint(user, 10000 * 1e18);

        uint256 predispatchAmount = 1000 * 1e18;
        // After transferring to dispatcher: 1% fee = dispatcher receives 990
        uint256 dispatcherReceived = predispatchAmount - (predispatchAmount * 100) / 10000;
        // After dispatcher transfers to gateway: another 1% fee = gateway receives ~980.1
        uint256 gatewayReceived = dispatcherReceived - (dispatcherReceived * 100) / 10000;

        // Predispatch: send FOT to dispatcher, the "call" is a no-op (empty calls array)
        TokenInfo[] memory predispatchAssets = new TokenInfo[](1);
        predispatchAssets[0] = TokenInfo({token: bytes32(uint256(uint160(address(fot)))), amount: predispatchAmount});

        // The predispatch call is an empty Call[] dispatch (no-op, tokens just sit on dispatcher)
        Call[] memory emptyCalls = new Call[](0);
        bytes memory predispatchCall = abi.encode(emptyCalls);

        // Inputs: expect the FOT that lands on dispatcher after predispatch
        TokenInfo[] memory inputs = new TokenInfo[](1);
        inputs[0] = TokenInfo({token: bytes32(uint256(uint160(address(fot)))), amount: dispatcherReceived});

        TokenInfo[] memory outputAssets = new TokenInfo[](1);
        outputAssets[0] = TokenInfo({token: bytes32(uint256(uint160(address(dai)))), amount: 500 * 1e18});

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
            predispatch: DispatchInfo({assets: predispatchAssets, call: predispatchCall}),
            inputs: inputs,
            output: output
        });

        vm.startPrank(user);
        fot.approve(address(intentGateway), predispatchAmount);
        intentGateway.placeOrder(order, bytes32(0));
        vm.stopPrank();

        // Gateway should hold only what it actually received (double fee-on-transfer)
        assertEq(fot.balanceOf(address(intentGateway)), gatewayReceived, "Gateway should hold double-taxed amount");

        // Reconstruct commitment
        order.user = bytes32(uint256(uint160(user)));
        order.source = host.host();
        order.nonce = 0;
        order.inputs[0].amount = gatewayReceived; // mutated to actual received
        bytes32 commitment = keccak256(abi.encode(order));

        assertEq(
            intentGateway._orders(commitment, address(fot)),
            gatewayReceived,
            "Escrow should match actual received after double transfer fee"
        );
    }
```

**File:** evm/tests/foundry/IntentGatewayV2SameChainTest.sol (L2689-2730)
```text
/// @dev ERC20 with a configurable transfer fee (in basis points).
contract FeeOnTransferToken {
    string public name = "FeeOnTransferToken";
    string public symbol = "FOT";
    uint8 public decimals = 18;
    uint256 public totalSupply;
    uint256 public feeBps;

    mapping(address => uint256) public balanceOf;
    mapping(address => mapping(address => uint256)) public allowance;

    constructor(uint256 _feeBps) {
        feeBps = _feeBps;
    }

    function mint(address to, uint256 amount) external {
        balanceOf[to] += amount;
        totalSupply += amount;
    }

    function approve(address spender, uint256 amount) external returns (bool) {
        allowance[msg.sender][spender] = amount;
        return true;
    }

    function transfer(address to, uint256 amount) external returns (bool) {
        return _transfer(msg.sender, to, amount);
    }

    function transferFrom(address from, address to, uint256 amount) external returns (bool) {
        uint256 allowed = allowance[from][msg.sender];
        if (allowed != type(uint256).max) {
            allowance[from][msg.sender] = allowed - amount;
        }
        return _transfer(from, to, amount);
    }

    function _transfer(address from, address to, uint256 amount) internal returns (bool) {
        uint256 fee = (amount * feeBps) / 10_000;
        uint256 received = amount - fee;
        balanceOf[from] -= amount;
        balanceOf[to] += received;
```
