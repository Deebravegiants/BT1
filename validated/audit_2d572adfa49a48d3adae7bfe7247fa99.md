## Analysis

The Tron deployment of `IntentGatewayV2` diverges from the main EVM `IntentGatewayV2` in exactly the way the fee-on-transfer report describes: it computes and stores the escrowed/committed amount **before** verifying what the contract actually received from the ERC20 transfer.

### Root cause

In `evm/tron/contracts/apps/IntentGatewayV2.sol::placeOrder()`, the reduced (post-protocol-fee) input amounts used both for the EIP-712/commitment hash and for crediting the escrow ledger are derived straight from `order.inputs[i].amount` — the user-supplied amount — not from any pre/post balance measurement: [1](#0-0) 

For every input token, the contract calls `safeTransferFrom(msg.sender, address(this), order.inputs[i].amount)` and then unconditionally does `_orders[commitment][token] += reducedInputs[i].amount;`, i.e. the accounting entry equals the requested amount minus the protocol fee, with no adjustment for a fee-on-transfer token that would deliver less than `order.inputs[i].amount` to the contract.

This is the same class of bug that the report flags in Allo's `_fundPool`, and it contrasts directly with the fix already present in the primary EVM `IntentGatewayV2.sol::placeOrder()` (and mirrored in its foundry tests), which explicitly snapshots `balanceOf(address(this))` before/after the transfer and mutates `order.inputs[i].amount` to the *actual received amount* before computing the commitment and crediting escrow: [2](#0-1) [3](#0-2) 

The Tron contract's `withdraw()` function later pays out exactly `body.tokens[i].amount` (the same over-stated, fee-uncorrected amount) to the beneficiary/refund recipient on both the redeem and refund paths: [4](#0-3) 

### Title
Fee-on-transfer tokens cause `_orders` escrow over-accounting and insolvency in Tron `IntentGatewayV2.placeOrder` - (File: evm/tron/contracts/apps/IntentGatewayV2.sol)

### Summary
The Tron variant of `IntentGatewayV2` credits the order escrow mapping `_orders[commitment][token]` with the user-requested (fee-reduced-by-protocol-fee) input amount rather than the amount actually received via `safeTransferFrom`. For fee-on-transfer (FOT) ERC20 tokens, the contract's real token balance will be permanently less than the sum of all outstanding `_orders` entries for that token.

### Finding Description
`placeOrder()` computes `reducedInputs[i].amount` from `order.inputs[i].amount` (minus protocol fee only) and immediately writes `_orders[commitment][token] += reducedInputs[i].amount` around the `safeTransferFrom` call, with no balance check before/after the transfer: [1](#0-0) 
If `token` deducts a transfer fee, the gateway contract actually receives less than `order.inputs[i].amount`, yet the escrow ledger (and the EIP-712 commitment hash used for cross-chain proofs) reflects the un-discounted figure. Any unprivileged user can call `placeOrder` with an arbitrary ERC20, including a FOT token, making this fully reachable without any privileged role.

### Impact Explanation
Because `withdraw()` (invoked both from same-chain cancellation and from cross-chain `RedeemEscrow`/`RefundEscrow` `onAccept` handling) pays out `body.tokens[i].amount` taken from the order/commitment data rather than checking the contract's actual token balance, the sum of all escrow claims can exceed the contract's real balance of that token. This creates a shortfall (insolvency) where later legitimate withdrawals/redemptions for other orders of the same token can fail or be partially unfulfillable — a permanent freezing of some users' funds — since first-claimed withdrawals will drain real balance that was actually owed to other orders' depositors.

### Likelihood Explanation
Any unprivileged caller can trigger this simply by using a fee-on-transfer token as an order input; no special permissions, races, or governance actions are required. The bug is deterministic for any such token and the main EVM contract already had to be patched for exactly this scenario, confirming it is a realistic and expected token class in this protocol's design space.

### Recommendation
Mirror the fix already applied to `evm/src/apps/IntentGatewayV2.sol`: measure `IERC20(token).balanceOf(address(this))` immediately before and after each `safeTransferFrom` call, use the delta as the actual received amount, mutate `order.inputs[i].amount` accordingly before computing `reducedInputs` and the commitment hash, and credit `_orders[commitment][token]` with the fee-corrected value.

### Proof of Concept
1. Deploy a fee-on-transfer ERC20 token (e.g., 1% fee) and mint balance to a user.
2. User approves and calls `IntentGatewayV2(tron).placeOrder(order, graffiti)` with `order.inputs[0] = {token: FOT, amount: 1000e18}` and `protocolFeeBps = 0`.
3. Contract executes `safeTransferFrom(user, address(this), 1000e18)`, but only `990e18` actually lands in the contract due to the 1% transfer fee.
4. `_orders[commitment][FOT]` is nonetheless set to `1000e18` (== `reducedInputs[0].amount`), a `10e18` overstatement versus the real balance.
5. Repeating this with multiple orders accumulates a growing gap between `sum(_orders[...])` and `IERC20(FOT).balanceOf(address(this))`; once enough redemptions/refunds are processed, some order's `withdraw()` call will move more tokens out than the contract holds for that token, reverting or (if other tokens/ETH cover the call accidentally) draining balance owed to other orders — freezing funds for the affected order owners.

### Citations

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

**File:** evm/tests/foundry/IntentGatewayV2SameChainTest.sol (L2440-2479)
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
```
