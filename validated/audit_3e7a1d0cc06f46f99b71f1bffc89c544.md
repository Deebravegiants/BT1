### Title
Fee-on-transfer input tokens cause escrow over-crediting and insolvency in Tron `IntentGatewayV2.placeOrder()` - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The Tron variant of `IntentGatewayV2.placeOrder()` computes the escrowed token amount from the user-specified `order.inputs[i].amount` (minus protocol fee) and then separately pulls the same nominal amount via `safeTransferFrom`, without ever checking how much the contract actually received. Unlike the canonical EVM `IntentGatewayV2.sol`, which was hardened against fee-on-transfer tokens by snapshotting balances before/after transfer, the Tron port never adopted that fix.

### Finding Description
In `evm/tron/contracts/apps/IntentGatewayV2.sol::placeOrder()`, the escrow credit and the commitment hash are derived purely from the caller-supplied `order.inputs[i].amount`: [1](#0-0) 

Then, in the token-transfer branch, the exact nominal `order.inputs[i].amount` is pulled via `safeTransferFrom`, and the escrow ledger `_orders[commitment][token]` is incremented by `reducedInputs[i].amount` — a value derived from the nominal amount, not from any balance check: [2](#0-1) 

If the input token deducts any transfer fee (fee-on-transfer / deflationary token, or a rebasing/tax token whose behavior changes post-deployment — a realistic scenario on Tron given TRC20 tokens frequently implement configurable fee/blacklist logic, e.g. USDT-TRC20's admin-controlled fee fields), the gateway's actual token balance increase will be strictly less than `order.inputs[i].amount`. The escrow accounting, however, still records the full (fee-un-adjusted) amount as owed.

This is the exact bug class from the referenced report: code assumes `amountSent == amountReceived` for arbitrary whitelisted-by-user ERC20/TRC20 tokens, and uses the pre-transfer amount in subsequent accounting instead of a balance-diff check.

Contrast this with the already-patched sibling contract `evm/src/apps/IntentGatewayV2.sol`, which explicitly guards against this: [3](#0-2) 
and has dedicated regression tests (`testPlaceOrder_FeeOnTransferToken_EscrowMatchesReceived`, etc.) proving the intended behavior: [4](#0-3) 

The Tron contract has no equivalent balance-diff logic anywhere in `placeOrder()`.

### Impact Explanation
Each `placeOrder()` call using a fee-charging input token creates an escrow entry (`_orders[commitment][token]`) that overstates the tokens actually custodied by the gateway by the fee amount. Because escrow bookkeeping across *all* orders for a token shares the same underlying token balance, this shortfall accumulates across orders. When solvers later fill orders and call `_withdraw`/settlement paths that transfer out the recorded escrow amount (`IERC20(token).safeTransfer(beneficiary, amount)`), the contract can become insolvent for that token — some legitimate withdrawal will revert or drain balance meant for other users' orders, permanently freezing funds for unrelated order participants. This is a fund-freezing/accounting-insolvency bug reachable by any unprivileged user submitting `placeOrder()` with such a token, matching the accepted "permanent freezing of funds" impact class.

### Likelihood Explanation
Likelihood is realistic but conditional: it requires an input token used in the whitelist/at the caller's discretion (the intent gateway is permissionless as to which ERC20/TRC20 the user chooses as input) to apply any transfer fee. TRC20 tokens (notably USDT-TRC20) commonly ship with admin-toggleable fee mechanisms even if currently set to zero, and the contract offers no allowlist restricting inputs to fee-free tokens. Given that the sibling EVM contract was already patched specifically for this exact scenario, the risk was previously identified as credible for this codebase.

### Recommendation
Apply the same balance-before/after pattern already used in `evm/src/apps/IntentGatewayV2.sol` to the Tron contract: measure `IERC20(token).balanceOf(address(this))` before and after each `safeTransferFrom`, and use the actual received delta (rather than the nominal `order.inputs[i].amount`) both for the escrow credit and for the commitment hash computation.

### Proof of Concept
1. Deploy the Tron `IntentGatewayV2` with a TRC20 token that charges a 1% transfer fee (or later has such a fee enabled via its admin, e.g. USDT-TRC20-style contracts).
2. User calls `placeOrder()` specifying `order.inputs[0].amount = 1000` of that token.
3. `placeOrder()` computes `reducedInputs[0].amount` from `1000` (minus protocol fee) and credits `_orders[commitment][token] += reducedInputs[0].amount` (e.g., ~1000 minus protocol fee).
4. `safeTransferFrom(msg.sender, address(this), 1000)` actually delivers only `990` tokens to the gateway due to the 1% fee.
5. The gateway now holds `990` tokens but has recorded escrow obligations totaling ~`1000` (minus protocol fee) for this order alone; repeating this with multiple orders compounds the shortfall.
6. When solver fills and settlement/withdrawal logic attempts to pay out the full recorded escrow amount, the gateway lacks sufficient token balance to honor all outstanding escrow entries, causing reverts or first-mover fund drains that freeze other users' rightful withdrawals.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L356-374)
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
