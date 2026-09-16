I found a direct analog. In the Tron variant of `IntentGatewayV2.placeOrder`, escrow accounting is credited from the *requested* amount rather than the *actual* amount received by the contract — exactly the `amountAfterFee` vs. real balance mismatch described in the report.

### Title
Fee-on-transfer / deflationary tokens cause escrow-ledger insolvency in Tron `IntentGatewayV2.placeOrder` - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The Tron port of `IntentGatewayV2.placeOrder` credits `_orders[commitment][token]` with the caller-declared (fee-adjusted-for-protocol-fee-only) amount, without ever verifying the token amount actually received by the contract via `balanceOf` diffing. For any ERC-20 with non-standard transfer behavior (fee-on-transfer, deflationary/rebasing), the gateway's internal escrow ledger will overstate the tokens it actually custodies.

### Finding Description
In the no-predispatch branch of `placeOrder`: [1](#0-0) 
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
        unchecked { ++i; }
    }
}
```
`reducedInputs[i].amount` is derived purely from `order.inputs[i].amount` minus the protocol fee bps — it is never reconciled against the token's actual `balanceOf(address(this))` delta. If the token deducts a transfer fee (or is rebasing/deflationary), the contract receives less than `order.inputs[i].amount`, yet the escrow ledger is credited as if the full amount arrived.

The predispatch branch has the same flaw: it computes `dust = balance - requiredAmount` and credits `reducedInputs[i].amount` to escrow based on the dispatcher's *pre-transfer* `balance`, without confirming the intermediate `transfer(address(this), balance)` call actually delivered `balance` tokens to `address(this)` (it may not, for a fee-on-transfer token): [2](#0-1) 

This is the exact same root-cause pattern as the referenced Allo.sol report: an accounting variable (`poolAmount` there, `_orders[commitment][token]` here) is incremented by a value computed from the *requested*/*declared* amount rather than the token amount actually custodied, so the ledger can promise more than the contract holds.

By contrast, the mainline EVM `IntentGatewayV2.sol` was hardened against exactly this class of bug — it measures `balanceOf` before and after each transfer and mutates `order.inputs[i].amount` to the actually-received value before computing fees/commitment/escrow: [3](#0-2) 
and has dedicated fee-on-transfer regression tests: [4](#0-3) 

The Tron variant was not updated to match this fix, reintroducing the vulnerability the main contract already patched.

Downstream, `withdraw()` pays out based on the (potentially inflated) `_orders[commitment][token]` ledger entry: [5](#0-4) 
```solidity
if (_orders[body.commitment][token] == 0) revert UnknownOrder();
...
_orders[body.commitment][token] -= amount;
```
Since the ledger can exceed the contract's real token balance across multiple orders sharing the same token, later `withdraw()` calls (whether for `RedeemEscrow`/solver payout or `RefundEscrow`/user refund) will either transfer less than legitimately escrowed elsewhere (draining balance meant for other orders) or hit `TransferFailed()`/revert once the real balance is exhausted, permanently freezing the escrow for whichever order settles last.

### Impact Explanation
This causes real insolvency in the intents escrow: the sum of all `_orders[commitment][token]` balances for a fee-on-transfer token can exceed the gateway's actual `balanceOf(this)`. This leads to either (a) some solver/user unable to redeem their legitimately filled/cancelled order because the tokens were never actually escrowed (permanent freezing of funds), or (b) a race where the first redeemers effectively drain tokens that were credited to other orders' ledger entries (funds theft/loss for later claimants). This is a Medium-severity, concrete loss-of-funds / freezing bug reachable directly by any unprivileged user calling `placeOrder` with an order that includes such a token.

### Likelihood Explanation
Any user (not just an admin) can call `placeOrder` with an arbitrary ERC-20 token address as an input asset — token allow-listing is not evident in this snippet. Fee-on-transfer and deflationary/rebasing tokens are common in the wild, and the mainline EVM contract's own test suite demonstrates the protocol explicitly anticipates and must handle such tokens. The Tron deployment's lack of the balance-diff fix makes this trivially triggerable by placing a single order using such a token — no special privileges or timing required.

### Recommendation
Apply the same fix used in `evm/src/apps/IntentGatewayV2.sol` to the Tron variant: after each `safeTransferFrom`/predispatch-sweep, measure `balanceOf(address(this))` before and after, mutate `order.inputs[i].amount` (and thus `reducedInputs[i].amount`) to reflect the actually-received amount, and only then compute the commitment hash and credit `_orders[commitment][token]`. Ensure the predispatch-sweep dust/escrow calculation also uses the real post-transfer balance of `address(this)`, not the pre-sweep `balanceOf(dispatcher)`.

### Proof of Concept
1. Deploy a fee-on-transfer ERC-20 (e.g., 1% fee, as in `FeeOnTransferToken` used in the EVM test suite) on the Tron-deployed `IntentGatewayV2`.
2. User calls `placeOrder` with `inputs[0] = {token: FOT, amount: 1000e18}` and `protocolFeeBps = 0` (no predispatch).
3. `safeTransferFrom(msg.sender, address(this), 1000e18)` executes; due to the 1% fee, the contract's actual `balanceOf` increases by only 990e18.
4. `_orders[commitment][FOT]` is nonetheless credited with `reducedInputs[0].amount = 1000e18` (since `reducedInputs == order.inputs` when `protocolFeeBps == 0`), a ledger figure 10e18 higher than what the contract actually holds.
5. If a second, unrelated order also escrows FOT tokens and is settled/withdrawn first, its `withdraw()` call succeeds by consuming part of the real balance that was meant to back the first order's 1000e18 ledger entry; the first order's later `withdraw()` then reverts with `TransferFailed()` once the real balance is insufficient, permanently freezing that user's/solver's funds. [1](#0-0) [5](#0-4)

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
