## Title
Fee-on-transfer tokens are not accounted for in `IntentGatewayV2.placeOrder`, causing inflated escrow accounting and permanent freezing of funds on the Tron gateway - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The Tron variant of `IntentGatewayV2.placeOrder` credits escrow (`_orders[commitment][token]`) with the user-requested amount (minus protocol fee) instead of the amount actually received via `safeTransferFrom`. For fee-on-transfer/deflationary tokens, the gateway's real token balance will be lower than the escrowed bookkeeping amount, so later `withdraw()` calls will attempt to transfer more tokens than the contract holds and revert, permanently freezing the escrowed funds — the same root-cause pattern as the Notional `TokenHandler.transfer`/`VaultConfiguration._redeem` mismatch cited in the report (nominal-amount accounting vs. actual-received-amount accounting diverging for fee-charging tokens).

### Finding Description
In the non-predispatch branch of `placeOrder`, tokens are pulled in with: [1](#0-0) 

```solidity
} else {
    for (uint256 i; i < inputsLen;) {
        if (order.inputs[i].amount == 0) revert InvalidInput();
        address token = address(uint160(uint256(order.inputs[i].token)));
        if (token == address(0)) {
            if (msgValue < order.inputs[i].amount) revert InsufficientNativeToken();
            msgValue -= order.inputs[i].amount;
        } else {
            IERC20(token).safeTransferFrom(msg.sender, address(this), order.inputs[i].amount);
        }

        // Store reduced amount (after protocol fees) in escrow
        _orders[commitment][token] += reducedInputs[i].amount;
        ...
``` [2](#0-1) 

`reducedInputs[i].amount` is derived purely from `order.inputs[i].amount` (the amount the user *specified*), reduced only by the protocol fee, never by any transfer fee the token itself may charge: [3](#0-2) 

The predispatch branch has the same issue — it computes `dust = balance - requiredAmount` for excess only, and still credits `reducedInputs[i].amount` into escrow regardless of what the contract actually holds: [4](#0-3) 

This is in stark contrast to the canonical EVM gateway (`evm/src/apps/IntentGatewayV2.sol`), which explicitly snapshots balances before/after the transfer and mutates `order.inputs[i].amount` to the *actual received* amount before computing the commitment and escrow, precisely to handle fee-on-transfer tokens: [5](#0-4) 

This divergence is also demonstrated by the dedicated fee-on-transfer regression tests that exist for the canonical gateway but have no Tron counterpart: [6](#0-5) 

When the escrow is later redeemed via `withdraw()` (triggered by `RedeemEscrow`/`RefundEscrow` in `onAccept`, or same-chain `cancelOrder`), the contract attempts to transfer the *bookkeeping* amount stored in `_orders[commitment][token]`, not the actual balance the contract holds: [7](#0-6) 

For any token with a transfer fee, the amount recorded in `_orders` will exceed the tokens actually sitting in the gateway contract, since `safeTransferFrom` delivers less than `order.inputs[i].amount` but the full (fee-adjusted) nominal amount is still credited to escrow.

### Impact Explanation
Because `withdraw()` uses `SafeERC20`/ERC20 `transfer` for the recorded escrow amount, once the real balance is insufficient the transfer reverts, permanently freezing the user's (and potentially the solver's) funds for that order — refunds via `cancelOrder`, cross-chain redemption via `onAccept`/`RedeemEscrow`, and refunds via `RefundEscrow` all funnel through the same `withdraw()` function and will all revert. This is a permanent freezing-of-funds condition reachable by any unprivileged user calling `placeOrder` with a fee-on-transfer input token, matching the "Unable to Recover Funds" impact class from the source report.

### Likelihood Explanation
Likelihood depends on whether fee-on-transfer tokens are supported as valid `order.inputs[i].token` values on the Tron deployment. No allowlist/denylist for token types is visible in `placeOrder`, `withdraw`, or `_params`, so any ERC20 (including fee-on-transfer/deflationary tokens, common in various ecosystems) can be placed as an input, making this directly reachable from a single `placeOrder` transaction by any user/intent solver without any privileged role.

### Recommendation
Mirror the canonical `evm/src/apps/IntentGatewayV2.sol` behavior in the Tron contract: measure the gateway's actual token balance before and after each `safeTransferFrom` (and after the predispatch sweep), and use the *actual received* amount — not the user-requested amount — both for the escrow accounting (`_orders[commitment][token]`) and for the commitment hash computation, before applying protocol-fee reduction.

### Proof of Concept
1. Deploy a fee-on-transfer ERC20 (e.g. 1% fee) and register it as a valid input token for `IntentGatewayV2` (Tron).
2. User calls `placeOrder` with `order.inputs[0] = {token: FOT, amount: 1000e18}`, approving 1000e18.
3. `safeTransferFrom` delivers only 990e18 to the gateway (`IERC20(token).safeTransferFrom(msg.sender, address(this), 1000e18)` at line 459), but `_orders[commitment][token] += reducedInputs[i].amount` credits ~1000e18 (minus protocol fee only) at line 463.
4. Gateway's real `FOT.balanceOf(address(this))` is 990e18 while `_orders[commitment][token]` records ~1000e18 (or the protocol-fee-reduced equivalent, still above 990e18 for any nonzero-fee token).
5. On cancellation (`cancelOrder` → `withdraw`) or cross-chain redemption (`onAccept` → `withdraw`), the contract attempts `IERC20(token).transfer(beneficiary, amount)` for `amount` read from `_orders[commitment][token]` (~1000e18), which reverts due to insufficient balance, permanently freezing the escrowed 990e18.

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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L437-441)
```text
                uint256 dust = balance - requiredAmount;
                if (dust > 0) emit DustCollected(token, dust);

                // Store reduced amount (after protocol fees) in escrow
                _orders[commitment][token] += reducedInputs[i].amount;
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

**File:** evm/src/apps/IntentGatewayV2.sol (L312-323)
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
```

**File:** evm/tests/foundry/IntentGatewayV2SameChainTest.sol (L2441-2494)
```text
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
