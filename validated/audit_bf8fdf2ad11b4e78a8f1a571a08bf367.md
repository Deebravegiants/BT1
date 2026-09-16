## Finding

Based on my research, I found a valid analog in the Tron variant of the IntentGateway contract.

### Title
Fee-on-transfer tokens can under-fund escrow accounting in `IntentGatewayV2.placeOrder`, permanently locking other users' funds - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The original report concerns `Wallet.refund` crediting a fixed internal accounting amount while actually receiving a different amount from a non-standard token, causing funds to become permanently stuck. The Tron deployment of `IntentGatewayV2.placeOrder` has the same root-cause bug class: it credits the escrow ledger with the *nominal requested amount* rather than the *amount actually received* from `safeTransferFrom`, so a fee-on-transfer (or any token that delivers less than the transferred amount) token silently under-funds the pool relative to what is recorded as owed.

### Finding Description
In `evm/tron/contracts/apps/IntentGatewayV2.sol`, `placeOrder` computes the commitment and escrow amounts directly from the caller-supplied `order.inputs[i].amount`, then simply calls `safeTransferFrom` and increments `_orders[commitment][token]` by `reducedInputs[i].amount` — without ever checking the contract's actual token balance before/after the transfer: [1](#0-0) 

By contrast, the primary EVM implementation (`evm/src/apps/IntentGatewayV2.sol`) explicitly patches this exact issue by measuring the balance before and after `safeTransferFrom` and mutating `order.inputs[i].amount` to the *actual received* amount before computing fees, the commitment, and the escrow credit: [2](#0-1) [3](#0-2) 

This divergence is confirmed by dedicated regression tests in the primary EVM codebase (`testPlaceOrder_FeeOnTransferToken_EscrowMatchesReceived`, `testPlaceOrder_FeeOnTransferToken_WithProtocolFee`) which assert escrow must equal actual received balance, not the nominal amount: [4](#0-3) 

The Tron contract has no equivalent balance-based correction, so `_orders[commitment][token]` will over-state the tokens actually escrowed whenever the input token takes a transfer fee (or otherwise delivers less than the nominal `amount`).

### Impact Explanation
Because escrow bookkeeping is a shared per-token ledger inside one contract (not a per-order token custody), when a fee-on-transfer token order under-funds the contract relative to its recorded escrow, later withdrawals for *that* order (via `RedeemEscrow`/`RefundEscrow` in `withdraw()`) will draw down the contract's actual token balance beyond what that specific order actually contributed, effectively spending balance that belongs to other orders' escrows of the same token: [5](#0-4) 
Once the shared pool is depleted this way, other legitimate orders for the same token will find `IERC20.transfer` failing (insufficient balance) or reverting via `TransferFailed`, permanently freezing their escrowed funds and requiring a privileged upgrade/admin intervention to remediate — the same class of impact (funds "stuck... require an upgrade to remove them") described in the original report.

### Likelihood Explanation
`placeOrder` is a fully public, unprivileged, single-transaction entry point reachable by any token bridger/user. Fee-on-transfer and deflationary ERC20/TRC20 tokens are common in production DeFi ecosystems, so the precondition (a listed input token that takes a transfer fee) is realistic rather than contrived; the primary EVM contract's own test suite treats this exact scenario as an expected, must-handle case.

### Recommendation
Apply the same fix used in the primary EVM `IntentGatewayV2.sol`: measure the contract's token balance before and after `safeTransferFrom` for each input, mutate `order.inputs[i].amount` (and consequently the commitment and escrow credit) to the actual received amount, before computing protocol fees and crediting `_orders`.

### Proof of Concept
1. Deploy `IntentGatewayV2` (Tron variant) and register a fee-on-transfer TRC20 token (e.g., 1% fee) as a valid input asset.
2. User A calls `placeOrder` with `inputs[0].amount = 1000` of the fee-on-transfer token. The contract actually receives only 990 tokens via `safeTransferFrom`, but `_orders[commitmentA][token]` is credited with `1000` (minus protocol fee if any) — i.e., an amount the contract does not actually hold for this order.
3. User B independently places a normal (non-fee) order for the same token, escrowing e.g. 500 tokens; contract's real balance for the token is now `990 + 500 = 1490`, but total recorded escrow obligations are `1000 + 500 = 1500`.
4. When order A is filled/redeemed, `withdraw()` transfers out the full recorded `1000` from the shared token balance, leaving only `490` for order B's `500` obligation.
5. When order B attempts to redeem, the `IERC20.transfer` call fails (`TransferFailed`) because the contract's balance is insufficient, permanently freezing user B's escrowed funds. [6](#0-5)

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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L691-723)
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

        // redeem tx fees
        uint256 fees = _orders[body.commitment][TRANSACTION_FEES];
        if (fees > 0) {
            address feeToken = IDispatcher(host()).feeToken();
            (bool success,) = feeToken.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, fees));
            if (!success) revert TransferFailed();
            delete _orders[body.commitment][TRANSACTION_FEES];
        }
```

**File:** evm/src/apps/IntentGatewayV2.sol (L230-234)
```text
        // Phase 1: Transfer tokens and record actual received amounts.
        // For fee-on-transfer tokens, the gateway receives less than the requested amount.
        // We mutate order.inputs to reflect actual received so the commitment and escrow
        // are consistent with what the gateway holds.
        uint256 msgValue = msg.value;
```

**File:** evm/src/apps/IntentGatewayV2.sol (L312-328)
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
