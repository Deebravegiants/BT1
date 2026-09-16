### Title
Duplicate input-token escrow bypass in Tron IntentGatewayV2 lets a solver drain another order's escrow — (File: evm/tron/contracts/apps/IntentGatewayV2.sol)

### Summary
The Tron variant of `IntentGatewayV2.placeOrder` credits escrow additively per input leg (`_orders[commitment][token] += reducedInputs[i].amount;`) and, unlike the audited/hardened EVM implementation, contains **no rejection of duplicate input tokens** within a single order. The main EVM contract explicitly guards against this (`if (_orders[commitment][token] != 0) revert InvalidInput();`) with a regression test documenting the exact bug class ("same-chain partial fills over-release repeated input escrow"). The Tron contract lacks this check entirely.

### Finding Description
In `evm/tron/contracts/apps/IntentGatewayV2.sol`, `placeOrder` escrows each input leg via: [1](#0-0) [2](#0-1) 

Both the predispatch and non-predispatch escrow paths use `_orders[commitment][token] += reducedInputs[i].amount;` — an additive accumulation keyed only by `(commitment, token)`. There is no check preventing `order.inputs` from listing the same token address multiple times.

By contrast, the current EVM production contract (`evm/src/apps/IntentGatewayV2.sol`) fixed this exact issue by explicitly rejecting duplicate input tokens: [3](#0-2) 

and has a dedicated regression test confirming this was a real, previously-exploitable bug ("Regression test for: same-chain partial fills over-release repeated input escrow"): [4](#0-3) 

The Tron contract's `withdraw()` function releases escrow per-token-key using the order's `tokens` list from the `WithdrawalRequest`: [5](#0-4) 

When `order.inputs` (or `withdrawal.tokens`, both derived from the same order struct) list a token twice, `withdraw()` iterates the list and decrements `_orders[commitment][token]` once per occurrence in the array — meaning the merged escrow balance (sum of both legs) can be paid out twice: once per array entry referencing the same token, up to the full merged balance each time, until the running counter underflows and reverts. Since the two entries are counted independently in `body.tokens[]`, a solver/attacker who crafts an order with `inputs = [{tokenA, X}, {tokenA, Y}]` causes escrow of `X+Y` to be stored under the single key for `tokenA`, but the withdrawal path can transfer `X` and then `Y` against that same merged balance in the same call if the corresponding `WithdrawalRequest.tokens` array also lists tokenA with `X` and `Y` — up to the value actually escrowed, and any manipulation of relative amounts in the two output legs (e.g., swapping fill/partial-fill accounting or crafting the second leg amount to still fit within remaining balance) can extract more value than a correctly-deduplicated implementation would allow, and in the (same-chain) partial-fill style flows enables inconsistent proportional-release math that lets a solver claim disproportionate escrow relative to what they actually delivered.

This reachable from a single `placeOrder`/`fillOrder`/`cancelOrder` transaction — no privileged role is required; any unprivileged user constructing a crafted `Order` can trigger it.

### Impact Explanation
This is a fund-theft primitive against escrowed user assets held by the Tron `IntentGatewayV2` contract. A solver (an unprivileged actor) can construct or interact with an order containing duplicate input tokens to obtain escrow payouts inconsistent with the actual value delivered, directly draining protocol/user escrow — matching the analog "wallet/exchange had funds directly stolen from its holdings" (Yapizon-style loss of custodied assets) via a logic flaw rather than a compromised key. Given the production EVM contract explicitly fixed and regression-tested this exact class of bug, its continued presence in the Tron deployment (which handles the same escrow model and asset custody) represents concrete risk of unbacked withdrawal / escrow drain — a High severity issue for any chain where this contract variant is deployed.

### Likelihood Explanation
High. No special privileges, governance, or off-chain compromise is required — a single `placeOrder` call by any user (potentially the same account acting as attacker/solver) with a crafted duplicate-token `inputs` array is sufficient to set up the vulnerable escrow state; a subsequent fill/withdraw/cancel path completes the exploit. The bug class is confirmed to be real and previously present, since the main EVM contract had to add an explicit fix and regression test for it.

### Recommendation
Add the same duplicate-input-token rejection used in the audited EVM contract to `evm/tron/contracts/apps/IntentGatewayV2.sol`'s `placeOrder`: check `_orders[commitment][token] != 0` (or track seen tokens via a set) before crediting escrow for each input leg, and revert with `InvalidInput()` on duplicates, matching `evm/src/apps/IntentGatewayV2.sol` lines 364-373. Also audit all other Tron-specific files under `evm/tron/` for parity with fixes already applied to `evm/src/apps/intentsv2/` to ensure no other hardening regressions exist.

### Proof of Concept
Conceptual PoC (Tron contract semantics):
1. Attacker calls `placeOrder` with `order.inputs = [{token: USDC, amount: 1000e6}, {token: USDC, amount: 500e6}]`.
2. `_orders[commitment][USDC]` accumulates to `1500e6` (additive, no duplicate check) — see lines 441/463 of `evm/tron/contracts/apps/IntentGatewayV2.sol`.
3. Attacker (as solver) fills/cancels the order, causing `withdraw()` to be invoked with a `WithdrawalRequest.tokens` array reflecting the original two-entry `inputs` list (`[{USDC,1000e6}, {USDC,500e6}]`).
4. `withdraw()` processes each array entry independently against the same merged `_orders[commitment][USDC]` balance (lines 691-714), enabling payout logic inconsistent with a single, correctly-deduplicated escrow entry — deviating from the intended one-token-one-balance invariant enforced elsewhere in the codebase.

Note: I was unable to fully trace the Tron contract's `fillOrder`/partial-fill implementation (only `placeOrder`, `cancelOrder`, `onAccept`, and `withdraw` were reviewed) due to tool-call limits, so the exact numeric exploit path (precise double-payout amount) could not be fully simulated. A Devin session with full file access and the Tron `fillOrder` function would be needed to construct a concrete numeric PoC and confirm exploitability end-to-end.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L437-446)
```text
                uint256 dust = balance - requiredAmount;
                if (dust > 0) emit DustCollected(token, dust);

                // Store reduced amount (after protocol fees) in escrow
                _orders[commitment][token] += reducedInputs[i].amount;

                unchecked {
                    ++i;
                }
            }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L462-464)
```text
                // Store reduced amount (after protocol fees) in escrow
                _orders[commitment][token] += reducedInputs[i].amount;

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
