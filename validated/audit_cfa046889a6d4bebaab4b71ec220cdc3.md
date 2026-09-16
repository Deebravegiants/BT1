## Finding

### Title
IntentGatewayV2 on Tron fails to account for fee-on-transfer tokens in `placeOrder`, causing escrow insolvency - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The Tron deployment of `IntentGatewayV2` credits the internal escrow ledger `_orders` with the *requested* input amount (minus protocol fee) instead of the amount the contract *actually receives* from `safeTransferFrom`. If any input token deducts a fee on transfer (the exact class of risk called out in the report for USDC, an upgradeable stablecoin whose transfer semantics are not permanently guaranteed), the gateway will record more collateral in escrow than it physically holds.

### Finding Description
In the non-predispatch branch of `placeOrder`, the gateway transfers tokens from the user and then unconditionally adds the pre-computed `reducedInputs[i].amount` (derived from `order.inputs[i].amount`, the amount the user *requested* to send) to escrow, without verifying the actual balance change: [1](#0-0) 

Compare this to the canonical (non-Tron) `IntentGatewayV2.sol`, which was hardened against this exact issue by snapshotting `balanceOf` before and after the transfer and mutating `order.inputs[i].amount` to the actually-received delta before it is used to compute the commitment and credit escrow: [2](#0-1) 

The predispatch branch of the same Tron file has an analogous gap: dust is computed against the dispatcher's balance, but the amount credited to escrow (`reducedInputs[i].amount`) is still derived from the original requested `order.inputs[i].amount`, not the amount that ultimately lands in the gateway after the final sweep transfer — so a second, uncompensated transfer-fee application on that sweep silently under-funds escrow relative to what was credited: [3](#0-2) 

The Solidity/EVM test suite explicitly documents and verifies the fix in the mainline contract for exactly this bug class (fee-on-transfer tokens), confirming the maintainers are aware of and have patched the risk there, but the parallel Tron contract does not carry the fix: [4](#0-3) 

### Impact Explanation
Any unprivileged user can call `placeOrder` on the Tron `IntentGatewayV2` with a fee-on-transfer ERC20/TRC20 input token (or any token that later becomes deflationary, mirroring the USDC upgrade risk cited in the report). The contract will credit `_orders[commitment][token]` with an amount larger than what it actually holds. Because escrowed balances back solver fills, refunds/cancellations, and cross-chain redemption of escrow, this creates a shortfall: the gateway's ledger promises more tokens than exist in its balance, which can cause later legitimate orders/refunds for the same token to fail or be under-collateralized, and in aggregate lets the contract become insolvent for that token — a permanent loss/freezing of funds for other users of the same escrow pool.

### Likelihood Explanation
Likelihood is contingent on an input token actually implementing a transfer fee (currently disclaimed for supported tokens), matching the report's own framing — the risk materializes if/when a currently-fee-free token (e.g., USDC-like assets) is upgraded to charge fees, or if a fee-on-transfer token is added to the supported input set. Given IntentGatewayV2 is designed to be permissionless with arbitrary user-supplied `TokenInfo.token` addresses in `order.inputs`, no governance action is required to trigger it once such a token is used as input — only a single `placeOrder` transaction.

### Recommendation
Apply the same fix already present in `evm/src/apps/IntentGatewayV2.sol` to `evm/tron/contracts/apps/IntentGatewayV2.sol`: snapshot `IERC20(token).balanceOf(address(this))` (or the dispatcher's balance, in the predispatch path) before and after each `safeTransferFrom`/sweep, and use the measured delta — not the caller-specified amount — when computing `reducedInputs`, the commitment hash, and the escrow credit in `_orders`.

### Proof of Concept
1. Deploy a fee-on-transfer TRC20 token (e.g. 1% fee, matching `FeeOnTransferToken` used in `evm/tests/foundry/IntentGatewayV2SameChainTest.sol`).
2. User calls `placeOrder` on the Tron `IntentGatewayV2` with `order.inputs[0] = {token: FOT, amount: 1000e18}` and approves the gateway for `1000e18`.
3. `safeTransferFrom` only delivers `990e18` to the gateway (1% fee retained by the token), matching `evm/tron/contracts/apps/IntentGatewayV2.sol` lines 451-460.
4. Despite only holding `990e18`, `_orders[commitment][FOT]` is credited with `reducedInputs[0].amount`, computed from the full `1000e18` requested amount minus only the protocol fee — i.e., escrow records more than the gateway's actual FOT balance.
5. A solver later fills the order and/or a cancellation/refund attempts to pay out the escrowed amount, but the gateway lacks sufficient FOT balance to cover all outstanding escrow entries for that token, causing reverts or under-payment to legitimate order participants.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L387-446)
```text
        // escrow tokens
        uint256 msgValue = msg.value;
        if (order.predispatch.call.length > 0 && order.predispatch.assets.length > 0) {
            address dispatcher = _params.dispatcher;

            // Transfer all predispatch assets to the call dispatcher
            uint256 assetsLen = order.predispatch.assets.length;
            for (uint256 i; i < assetsLen;) {
                address token = address(uint160(uint256(order.predispatch.assets[i].token)));
                uint256 amount = order.predispatch.assets[i].amount;

                if (token == address(0)) {
                    if (amount > msgValue) revert InsufficientNativeToken();
                    msgValue -= amount;

                    (bool sent,) = dispatcher.call{value: amount}("");
                    if (!sent) revert InsufficientNativeToken();
                } else {
                    IERC20(token).safeTransferFrom(msg.sender, dispatcher, amount);
                }

                unchecked {
                    ++i;
                }
            }

            // Execute the call dispatcher with predispatch call
            ICallDispatcher(dispatcher).dispatch(order.predispatch.call);

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
