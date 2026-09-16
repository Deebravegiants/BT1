## Analysis Result

### Title
Fee-on-transfer tokens cause escrow over-crediting and gateway insolvency in Tron `IntentGatewayV2.placeOrder` - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The Tron variant of `IntentGatewayV2.placeOrder` escrows tokens using the user-declared `order.inputs[i].amount` (minus protocol fee) instead of verifying the amount actually received by the contract. Unlike the mainline EVM `IntentGatewayV2.sol`, which was hardened against fee-on-transfer tokens by measuring balance deltas, the Tron fork never adopted this fix.

### Finding Description
In `placeOrder`, the non-predispatch escrow path performs: [1](#0-0) 

`IERC20(token).safeTransferFrom(msg.sender, address(this), order.inputs[i].amount)` is called with no balance check before/after, and `_orders[commitment][token] += reducedInputs[i].amount` credits escrow using `reducedInputs[i].amount`, which is derived directly from the caller-supplied `order.inputs[i].amount` (see `originalAmount = order.inputs[i].amount` at line 362) rather than the tokens actually received by the gateway. [2](#0-1) 

The predispatch path has the same flaw: the "dust" calculation at line 437 (`balance - requiredAmount`) is only used for an event, while the actual escrow credit again uses `reducedInputs[i].amount`, not the real balance transferred to the gateway. [3](#0-2) 

This is exactly the bug class from the report: the contract trusts a caller-supplied amount for a token transfer instead of measuring the actual balance delta, so any token that takes a fee/tax on transfer causes the contract to record more tokens in escrow than it physically holds.

By contrast, the current mainline EVM contract explicitly guards against this by computing `order.inputs[i].amount = IERC20(token).balanceOf(address(this)) - balBefore` after the transfer: [4](#0-3) 

and has dedicated tests (`testPlaceOrder_FeeOnTransferToken*`) confirming the fix is intentional for that codebase, which underscores that its absence on the Tron fork is a real regression/gap rather than a deliberate design choice. [5](#0-4) 

### Impact Explanation
When `withdraw` later pays out on order fill or refund, it transfers `body.tokens[i].amount` (the escrowed, fee-inflated amount) out of the gateway's token balance and decrements the same amount from `_orders[commitment][token]`: [6](#0-5) 

Since the gateway's actual token balance is smaller than the aggregate escrowed amounts recorded across all fee-on-transfer orders, once enough such orders accumulate the contract will run out of real tokens before all escrow entries are paid out. Later legitimate users placing/filling/cancelling orders with the same fee-on-transfer token will have their withdrawal calls revert (insufficient balance) or, if paid out of order, will drain balance belonging to other users' escrowed orders — resulting in permanent freezing/loss of funds for some depositors. This is directly reachable by any unprivileged user calling `placeOrder` with a fee-on-transfer ERC-20 as an input token, with no special permissions required.

### Likelihood Explanation
Likelihood is Medium: it requires an input token that charges a transfer fee (a known, non-rare ERC-20 pattern), but requires no privileged access, no governance action, and no cross-chain proof forgery — a single `placeOrder` call with such a token is sufficient to create the escrow/balance mismatch. Repeated use compounds the shortfall over time.

### Recommendation
Mirror the fix already present in `evm/src/apps/IntentGatewayV2.sol`: measure the actual token balance received via a before/after `balanceOf` check (or return value of the sweep transfer) instead of trusting `order.inputs[i].amount`, and use that measured amount for both the fee calculation, commitment computation, and escrow credit. Apply the same fix to the predispatch/dust-sweep branch.

### Proof of Concept
1. Deploy a fee-on-transfer ERC-20 (e.g., 1% fee) and approve the Tron `IntentGatewayV2` for `1000e18`.
2. Call `placeOrder` with `order.inputs[0].amount = 1000e18`. The contract's actual balance increases by only `990e18` (fee deducted), but `_orders[commitment][token]` is credited with `1000e18` (minus any protocol fee, still based on the declared amount, not received amount).
3. Repeat with multiple orders. The sum of `_orders[...][token]` values across all orders will exceed `IERC20(token).balanceOf(address(gateway))`.
4. When solvers/beneficiaries call the withdrawal path (`withdraw`) for all orders sequentially, the last order(s) to be redeemed will fail due to insufficient token balance, permanently freezing those users' expected proceeds, or — if fill order matters — an attacker can front-run withdrawals to drain the shared balance ahead of others.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L361-370)
```text
            for (uint256 i; i < inputsLen;) {
                uint256 originalAmount = order.inputs[i].amount;
                uint256 protocolFee = (originalAmount * protocolFeeBps) / 10_000;
                uint256 reducedAmount = originalAmount - protocolFee;
                address token = address(uint160(uint256(order.inputs[i].token)));

                // Emit DustCollected for protocol fee if non-zero
                if (protocolFee > 0) emit DustCollected(token, protocolFee);

                reducedInputs[i] = TokenInfo({token: order.inputs[i].token, amount: reducedAmount});
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

**File:** evm/src/apps/IntentGatewayV2.sol (L319-323)
```text
                } else {
                    uint256 balBefore = IERC20(token).balanceOf(address(this));
                    IERC20(token).safeTransferFrom(msg.sender, address(this), order.inputs[i].amount);
                    order.inputs[i].amount = IERC20(token).balanceOf(address(this)) - balBefore;
                }
```

**File:** evm/tests/foundry/IntentGatewayV2SameChainTest.sol (L2497-2515)
```text
    function testPlaceOrder_FeeOnTransferToken_WithProtocolFee() public {
        IntentGatewayV2 gatewayWithFees = _deployGatewayProxy();
        Params memory intentParams = Params({
            host: address(host),
            dispatcher: address(dispatcher),
            solverSelection: false,
            surplusShareBps: SURPLUS_SHARE_BPS,
            protocolFeeBps: PROTOCOL_FEE_BPS, // 30 bps
            priceOracle: address(0)
        });
        gatewayWithFees.initialize(intentParams, new bytes[](0), address(0));

        FeeOnTransferToken fot = new FeeOnTransferToken(100); // 1% transfer fee
        fot.mint(user, 10000 * 1e18);

        uint256 inputAmount = 1000 * 1e18;
        uint256 receivedAfterTransferFee = inputAmount - (inputAmount * 100) / 10000; // 990
        uint256 protocolFee = (receivedAfterTransferFee * PROTOCOL_FEE_BPS) / 10000;
        uint256 expectedEscrow = receivedAfterTransferFee - protocolFee;
```
