### Title
Tron `IntentGatewayV2.placeOrder` escrows the pre-fee-on-transfer amount instead of actual tokens received - ([File: evm/tron/contracts/apps/IntentGatewayV2.sol])

### Summary
The Tron variant of `IntentGatewayV2.placeOrder` credits the escrow ledger (`_orders[commitment][token]`) with the user-specified/protocol-fee-adjusted input amount without ever verifying that this is the amount the contract actually received via `safeTransferFrom`. For fee-on-transfer ERC20 tokens, this causes the contract's internal accounting to overstate its real token balance, exactly the bug class described in the referenced Astaria finding.

### Finding Description
In the non-predispatch branch of `placeOrder`, tokens are pulled in with a plain `safeTransferFrom` call and the escrow is incremented using `reducedInputs[i].amount`, which is derived from `order.inputs[i].amount` (the amount requested by the user, only adjusted for the protocol fee) — not from any measured balance delta: [1](#0-0) 

Contrast this with the canonical EVM `IntentGatewayV2.sol` (and its `IntentsBase`/tests), which explicitly snapshots `balanceOf` before and after the transfer and mutates `order.inputs[i].amount` to the actual received amount before computing the commitment and crediting escrow: [2](#0-1) 

This exact fee-on-transfer handling is verified by dedicated tests on the mainline EVM implementation: [3](#0-2) 

The Tron contract lacks this balance-before/after measurement entirely in its default escrow path, meaning any fee-on-transfer or deflationary token will cause the gateway to record more tokens in `_orders[commitment][token]` than it physically holds. When the order is later filled and redeemed via `withdraw`, the beneficiary/solver is paid out `body.tokens[i].amount` (the overstated escrow value) via `safeTransfer`: [4](#0-3) 

Because the contract holds strictly less of the token than the sum of what it believes is escrowed across all outstanding orders, later withdrawals for other, legitimate orders using the same fee-on-transfer token can revert due to insufficient balance, or (if amounts are drawn from a shared pool of dust/other orders' balances) can result in first-come-first-served draining where later users permanently lose their escrowed funds.

### Impact Explanation
This breaks the core escrow invariant of the Intents module on Tron: recorded IOUs (`_orders[commitment][token]`) exceed the token balance actually custodied by the contract for any fee-on-transfer/deflationary asset. This leads to permanent freezing of funds for at least one order sharing the same token (the contract cannot pay out more than it holds) and potential loss of user or solver funds depending on withdrawal ordering. This satisfies "permanent freezing of funds" / broken accounting criteria for a Medium-severity finding.

### Likelihood Explanation
Likelihood is moderate: it requires a fee-on-transfer or deflationary ERC20 token to be used as an intent input on the Tron deployment. Since the gateway is permissionless and accepts any ERC20 address supplied by the order placer (`token = address(uint160(uint256(order.inputs[i].token)))`), an unprivileged user placing an order with such a token is sufficient to trigger the broken accounting — no special privileges are required, matching the reachability bar for this analog.

### Recommendation
Mirror the mainline EVM `IntentGatewayV2.sol` fix in the Tron variant: snapshot `IERC20(token).balanceOf(address(this))` before and after each `safeTransferFrom` call in `placeOrder` (both predispatch and direct-transfer branches), and use the measured delta — not the requested amount — to compute `reducedInputs`, the commitment hash, and the value credited to `_orders[commitment][token]`.

### Proof of Concept
1. Deploy a 1% fee-on-transfer ERC20 token (as in `FeeOnTransferToken` from the test suite) and mint it to a user on the Tron gateway deployment.
2. User calls `placeOrder` with `inputs[0].amount = 1000e18` for the fee-on-transfer token, with `protocolFeeBps = 0` for simplicity.
3. `safeTransferFrom(msg.sender, address(this), 1000e18)` executes, but the gateway's actual token balance only increases by `990e18` due to the 1% transfer fee.
4. `_orders[commitment][token]` is nonetheless incremented by `1000e18` (via `reducedInputs[i].amount == order.inputs[i].amount` since no protocol fee applies).
5. When this order and any other order sharing the same token are both redeemed via `withdraw`, the cumulative `safeTransfer` calls will attempt to pay out `1000e18` combined with other escrowed amounts, exceeding the `990e18` actually held, causing a revert (denial of withdrawal) for at least one legitimate order, or allowing an earlier withdrawer to drain funds that belong to a later one.

### Citations

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
