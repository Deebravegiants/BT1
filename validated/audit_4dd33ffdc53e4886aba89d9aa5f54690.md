### Title
Missing duplicate-token rejection in `placeOrder` allows corrupted escrow accounting on Tron `IntentGatewayV2` - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The Tron deployment of `IntentGatewayV2.placeOrder` never rejects duplicate input or output tokens within a single order, unlike the canonical EVM `IntentGatewayV2.sol`, which explicitly guards against both cases. This is the same bug class as the reported `announceLimitOrder` issue: a user is able to submit an order that references the same token more than once, which corrupts the per-commitment accounting used later for fills, cancellations, and cross-chain withdrawals.

### Finding Description
In the canonical EVM gateway, `placeOrder` explicitly rejects duplicate output tokens via transient-storage tracking, and rejects duplicate input tokens by checking `_orders[commitment][token] != 0` before writing escrow: [1](#0-0) [2](#0-1) 

The accompanying regression tests confirm this was a fix for a real bug class — "same-chain partial fills over-release repeated input escrow" and "same-chain partial fills prematurely finalize repeated output legs": [3](#0-2) [4](#0-3) 

The Tron contract `evm/tron/contracts/apps/IntentGatewayV2.sol`, which shares the same `_orders`, `_filled`, `Order` commitment, and withdrawal logic, has none of these duplicate-token checks. Its `placeOrder` simply loops over `order.inputs` and accumulates escrow with `+=`, with no check for repeated tokens: [5](#0-4) 

There is also no check anywhere for duplicate `order.output.assets` tokens before the order is emitted/committed.

The downstream `withdraw` function (used both for same-chain refunds/redeems and for the cross-chain `RedeemEscrow`/`RefundEscrow` `onAccept` handlers) iterates over `body.tokens` (which is `order.inputs`, taken directly from the user-supplied, non-fee-reduced order struct in the cancel path) and, for each entry, checks only that the escrow bucket for that token is non-zero before transferring the requested amount and decrementing: [6](#0-5) 

Because the per-token check is `_orders[body.commitment][token] == 0` (existence only, not sufficiency) rather than a comparison against the amount being withdrawn, and because `body.tokens` can legitimately contain the same token address multiple times (as duplicate entries in `order.inputs`), an attacker can craft an order whose `inputs` array lists the same token repeatedly with amounts that don't match how the escrow was actually accumulated (e.g. due to fee-reduction only applied on one path, or via mismatched original vs. reduced amounts in the cross-chain cancel flow at `evm/tron/contracts/apps/IntentGatewayV2.sol:536-539`, which packages `order.inputs` — not `reducedInputs` — into the `WithdrawalRequest`). This inconsistency between the fee-reduced amount actually escrowed and the original (un-reduced) amount used for withdrawal, compounded with duplicate tokens, breaks the 1:1 assumption that later fill/cancel code relies on, exactly analogous to how the audited `LimitOrder` contract's failure to reject duplicate tokens let a user manipulate `cancelLimitOrder` accounting for one of two same-token orders.

### Impact Explanation
Corrupted escrow accounting from duplicate-token orders can allow a user to withdraw more than was legitimately escrowed for a given commitment, or to desynchronize the amount released during `withdraw` from what protocol fees actually reduced it to — resulting in fund loss for the protocol/other counter-parties (solver or fee-token pool) or silently mismatched escrow bookkeeping that later fill/cancellation code assumes is 1:1 per token. This matches the "incorrect calculation" impact class in the source report and falls under theft/permanent freezing risk given multiple state-mutating fund-transfer paths (`withdraw`, `onAccept` for `RedeemEscrow`/`RefundEscrow`) depend on `order.inputs` never containing duplicate token entries.

### Likelihood Explanation
Any unprivileged user who can call `placeOrder` on the Tron `IntentGatewayV2` contract can trivially construct an `Order` with repeated `TokenInfo` entries for the same input or output token address — no special permissions or timing are required, only a valid `Order` struct submitted in a normal `placeOrder` transaction.

### Recommendation
Port the duplicate-token rejection logic from the canonical `evm/src/apps/IntentGatewayV2.sol::placeOrder` (both the input-token check at `_orders[commitment][token] != 0` before writing escrow, and the output-token duplicate check) into `evm/tron/contracts/apps/IntentGatewayV2.sol::placeOrder`, and audit `withdraw`/`cancelOrder` on Tron to ensure the `WithdrawalRequest.tokens` amounts are always the fee-reduced, escrowed amounts rather than the raw user-supplied `order.inputs`.

### Proof of Concept
1. On the Tron `IntentGatewayV2`, call `placeOrder` with `order.inputs = [ {token: USDC, amount: 1200}, {token: USDC, amount: 1000} ]` and matching outputs — the contract accepts this without reverting (contrast with `evm/src/apps/IntentGatewayV2.sol`, which reverts with `InvalidInput` per `testRevert_PlaceOrder_DuplicateInputTokens`, at `evm/tests/foundry/IntentGatewayV2SameChainTest.sol:2117-2148`).
2. Escrow is credited via repeated `_orders[commitment][USDC] += reducedInputs[i].amount` (`evm/tron/contracts/apps/IntentGatewayV2.sol:463`), merging both legs into a single bucket.
3. On cancellation from the source chain, `WithdrawalRequest.tokens` is built directly from `order.inputs` (the two duplicate, non-fee-reduced entries) at `evm/tron/contracts/apps/IntentGatewayV2.sol:536-539`, rather than the fee-reduced amounts used to credit escrow — the `withdraw` function then transfers per-entry amounts that don't correspond to what was actually escrowed, only verifying the bucket is non-zero (`evm/tron/contracts/apps/IntentGatewayV2.sol:700`), producing over- or under-release of escrowed funds relative to the true committed amount.

I was not able to fully trace a Tron `fillOrder`/`_fillSameChain` implementation within the explored snippets (only `onAccept`/`withdraw`/`cancelOrder` were located), so I cannot confirm whether an equivalent `_partialFills`-style over-release exists on the fill path for Tron; this is noted as an area requiring further verification with full file access.

### Citations

**File:** evm/src/apps/IntentGatewayV2.sol (L197-211)
```text
        // Reject duplicate output tokens
        uint256 outputsLen_ = order.output.assets.length;
        for (uint256 i; i < outputsLen_;) {
            bytes32 token = order.output.assets[i].token;
            assembly ("memory-safe") {
                if tload(token) {
                    mstore(0, 0xb4fa3fb3) // InvalidInput.selector
                    revert(0x1c, 0x04)
                }
                tstore(token, 1)
            }
            unchecked {
                ++i;
            }
        }
```

**File:** evm/src/apps/IntentGatewayV2.sol (L363-373)
```text
        // Phase 3: Credit escrow.
        for (uint256 i; i < inputsLen;) {
            address token = address(uint160(uint256(order.inputs[i].token)));
            // Reject duplicate input tokens
            if (_orders[commitment][token] != 0) revert InvalidInput();
            _orders[commitment][token] = reducedInputs[i].amount;

            unchecked {
                ++i;
            }
        }
```

**File:** evm/tests/foundry/IntentGatewayV2SameChainTest.sol (L2115-2148)
```text
    /// @notice Placing an order with duplicate input tokens must revert.
    /// Regression test for: same-chain partial fills over-release repeated input escrow.
    function testRevert_PlaceOrder_DuplicateInputTokens() public {
        // Two input legs both using USDC — this previously merged into one escrow bucket
        TokenInfo[] memory inputs = new TokenInfo[](2);
        inputs[0] = TokenInfo({token: bytes32(uint256(uint160(address(usdc)))), amount: 1200 * 1e6});
        inputs[1] = TokenInfo({token: bytes32(uint256(uint160(address(usdc)))), amount: 1000 * 1e6});

        TokenInfo[] memory outputAssets = new TokenInfo[](2);
        outputAssets[0] = TokenInfo({token: bytes32(uint256(uint160(address(dai)))), amount: 500 * 1e18});
        outputAssets[1] = TokenInfo({token: bytes32(uint256(uint160(address(dai)))), amount: 1000 * 1e18});

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
        usdc.approve(address(intentGateway), 2200 * 1e6);
        vm.expectRevert(IntentsBase.InvalidInput.selector);
        intentGateway.placeOrder(order, bytes32(0));
        vm.stopPrank();
    }
```

**File:** evm/tests/foundry/IntentGatewayV2SameChainTest.sol (L2238-2272)
```text
    /// @notice Placing an order with duplicate output tokens must revert.
    /// Regression test for: same-chain partial fills prematurely finalize repeated output legs.
    function testRevert_PlaceOrder_DuplicateOutputTokens() public {
        TokenInfo[] memory inputs = new TokenInfo[](2);
        inputs[0] = TokenInfo({token: bytes32(uint256(uint160(address(usdc)))), amount: 1000 * 1e6});
        inputs[1] = TokenInfo({token: bytes32(uint256(uint160(address(dai)))), amount: 500 * 1e18});

        // Two output legs both requesting DAI — shares one _partialFills bucket
        TokenInfo[] memory outputAssets = new TokenInfo[](2);
        outputAssets[0] = TokenInfo({token: bytes32(uint256(uint160(address(dai)))), amount: 400 * 1e18});
        outputAssets[1] = TokenInfo({token: bytes32(uint256(uint160(address(dai)))), amount: 600 * 1e18});

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
        usdc.approve(address(intentGateway), 1000 * 1e6);
        dai.approve(address(intentGateway), 500 * 1e18);
        vm.expectRevert(IntentsBase.InvalidInput.selector);
        intentGateway.placeOrder(order, bytes32(0));
        vm.stopPrank();
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
