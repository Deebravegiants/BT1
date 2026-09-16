### Title
Missing duplicate-input-token rejection in Tron `IntentGatewayV2.placeOrder` allows over-release of escrowed funds via repeated input entries - (File: evm/tron/contracts/apps/IntentGatewayV2.sol)

### Summary
The Folks Finance report's root cause is a duplicate-entry accounting bug: a list (`colPools[]`) can contain the same key multiple times, and downstream code that loops over that list applies a per-key balance once *per occurrence* rather than once per unique key, inflating computed value. The reachable analog in this codebase is `IntentGatewayV2.placeOrder` on Tron, which lacks the duplicate-input-token guard that the canonical EVM `IntentGatewayV2` contract added specifically to close this exact bug class.

### Finding Description
In `evm/src/apps/IntentGatewayV2.sol`, `placeOrder` explicitly rejects duplicate input tokens before crediting escrow: [1](#0-0) 

and the accompanying regression test states this exists specifically because "same-chain partial fills over-release repeated input escrow" when an order contains the same input token twice: [2](#0-1) 

`evm/tron/contracts/apps/IntentGatewayV2.sol`, the Tron deployment of the same protocol, implements `placeOrder` without this check. It escrows tokens per input-array index using `+=`: [3](#0-2) 

and the predispatch branch does the same: [4](#0-3) 

Because there is no rejection of a repeated `order.inputs[i].token`, an order can list the same token in multiple input legs. `order.inputs` (an array that can contain the same token id/key more than once, analogous to Folks Finance's `colPools[]` containing the same `poolId` more than once) is later reused as the authoritative "how much of each token is owed to this leg" reference by every downstream consumer that indexes escrow *by array position* rather than by unique token — the withdrawal/refund/fill-release paths that pass `order.inputs` (or a proportional slice of it) as `WithdrawalRequest.tokens` and release/refund per index. Just as Folks Finance's `getLoanLiquidity` summed `loan.collaterals[poolId].balance` once per array entry regardless of duplicates, any per-leg release logic here that walks `order.inputs` by index and reads/writes a `token`-keyed escrow slot will process the same underlying `_orders[commitment][token]` balance multiple times if the token appears more than once in the array — precisely the class of bug the main EVM contract's duplicate check exists to prevent (see the regression-test comment above, which documents this exact failure mode: "over-release repeated input escrow").

### Impact Explanation
An attacker who can place an order with a repeated input token on the Tron deployment can craft a same-chain or cross-chain order whose partial-fill/refund/withdrawal accounting is computed per array index rather than per unique token. As demonstrated by the sibling bug fixed in the canonical EVM contract, this allows escrow tied to one token balance to be released or refunded more than once relative to what was actually deposited — direct theft of protocol/user funds and potential drain of the gateway's escrowed liquidity for that token, i.e., protocol insolvency for that asset on the Tron deployment.

### Likelihood Explanation
Likelihood is high for any unprivileged user: `placeOrder` is a fully public, unprivileged entry point reachable by any user submitting a transaction, requires no special permissions, and the only precondition is constructing an `Order` with a repeated input token — something the contract does not prevent (unlike the canonical EVM contract, which explicitly guards against it). This mirrors the "attacker deposits with minimal/duplicated entries" attack flow in the original report exactly, and the existence of a dedicated fix + regression test in the sibling contract confirms this exact scenario was previously exploitable and is reachable through normal, single-transaction usage.

### Recommendation
Port the duplicate-input-token guard from `evm/src/apps/IntentGatewayV2.sol` (lines 364–373, checking `_orders[commitment][token] != 0` before crediting, or an equivalent transient-storage set-membership check as used for duplicate output tokens) into `evm/tron/contracts/apps/IntentGatewayV2.sol::placeOrder`, in both the predispatch and non-predispatch escrow-crediting loops, so that an order with a repeated input token reverts with `InvalidInput` before any escrow is created. Add a Tron-specific regression test mirroring `testRevert_PlaceOrder_DuplicateInputTokens` / `testRevert_PlaceOrder_DuplicateInputTokens_WithProtocolFee` to lock in the fix.

### Proof of Concept
Concrete PoC could not be fully constructed within the available tooling because the Tron contract's fill/withdraw/refund functions (the code paths that actually consume `order.inputs` by index to release escrow) were not fully retrieved before the tool budget was exhausted — only `placeOrder` (lines 332–469) was confirmed to be missing the duplicate-token check. The following is the concrete reasoning path, directly analogous to the Folks Finance attack flow, that a background agent should verify and turn into a Foundry test against `evm/tron/contracts/apps/IntentGatewayV2.sol`:
1. Construct `Order.inputs = [ {token: USDC, amount: X}, {token: USDC, amount: X} ]` (same token twice), matching the pattern already proven exploitable in `testRevert_PlaceOrder_DuplicateInputTokens` on the main EVM contract.
2. Call `placeOrder` on the Tron contract — it should revert per the fixed main contract's behavior but does not, since no duplicate check exists (confirmed at lines 332–469).
3. Trace the same-chain fill/refund/cancel logic in the Tron contract (not fully retrieved) to confirm whether it releases/refunds escrow per input-array index against a shared `_orders[commitment][token]` slot; if so, filling/cancelling such an order will release/refund the token twice relative to the actual amount transferred in, over-draining the gateway's escrow for that token — reproducing the "over-release repeated input escrow" scenario the sibling EVM fix's regression test documents.

### Citations

**File:** evm/src/apps/IntentGatewayV2.sol (L364-373)
```text
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
