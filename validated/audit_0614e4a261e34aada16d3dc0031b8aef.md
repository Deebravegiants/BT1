### Title
Missing duplicate-input-token check in Tron `IntentGatewayV2.placeOrder` allows double-accounted escrow credit for a single commitment - (File: evm/tron/contracts/apps/IntentGatewayV2.sol)

### Summary
The GMX report describes a class of bug where accounting keyed by "token" has no dedup/divisor safeguard, so when two conceptually distinct accounting legs collapse onto the same token key (`longToken == shortToken`), the same balance gets counted (and later paid out) twice. The `IntentGatewayV2` escrow-credit logic in this repo has exactly this bug class: two variants of the same contract exist, and only one of them guards against duplicate token keys in `order.inputs`.

### Finding Description
The canonical EVM implementation of `placeOrder` explicitly guards against a duplicate input token colliding on the same escrow-accounting key: [1](#0-0) 

```solidity
// Phase 3: Credit escrow.
for (uint256 i; i < inputsLen;) {
    address token = address(uint160(uint256(order.inputs[i].token)));
    // Reject duplicate input tokens
    if (_orders[commitment][token] != 0) revert InvalidInput();
    _orders[commitment][token] = reducedInputs[i].amount;
    ...
```

This `revert InvalidInput()` guard exists precisely because, as documented by the regression tests in the same repo, allowing the same token to appear as more than one input leg previously "merged into one escrow bucket" and caused "same-chain partial fills over-release repeated input escrow": [2](#0-1) 

The **Tron** fork of the same contract, `evm/tron/contracts/apps/IntentGatewayV2.sol`, implements the equivalent escrow-credit step differently — it accumulates with `+=` instead of asserting the slot is empty first, and has **no** duplicate-token rejection anywhere in `placeOrder`: [3](#0-2) 

```solidity
uint256 dust = balance - requiredAmount;
if (dust > 0) emit DustCollected(token, dust);

// Store reduced amount (after protocol fees) in escrow
_orders[commitment][token] += reducedInputs[i].amount;
...
} else {
    for (uint256 i; i < inputsLen;) {
        if (order.inputs[i].amount == 0) revert InvalidInput();
        address token = address(uint160(uint256(order.inputs[i].token)));
        ...
        // Store reduced amount (after protocol fees) in escrow
        _orders[commitment][token] += reducedInputs[i].amount;
        ...
```

No check like `if (_orders[commitment][token] != 0) revert InvalidInput();` exists in this file (confirmed by grep across the repo — the "Reject duplicate" comment/guard is present only in `evm/src/apps/IntentGatewayV2.sol` and `evm/src/apps/intentsv2/IntrinsicIntents.sol`, not in the Tron variant).

Because `order.inputs[i].token` values are attacker(user)-controlled at `placeOrder` time and the commitment hash is computed over the same `order.inputs` array (so a duplicate-token order is internally consistent and hashes correctly), a user can submit an order whose `inputs` array lists the same token address in two (or more) legs. Each leg is transferred in individually and correctly summed via `+=` into `_orders[commitment][token]`. This mirrors the GMX bug precisely: the escrow map is keyed by token, with no per-leg divisor/dedup, so when two "logically separate" legs collapse onto the same key, their accounting is combined, and this combined value is what later gets treated as a single settlement bucket by cross-chain `withdraw()`/refund flows and by `cancelOrder`'s existence check: [4](#0-3) 

This makes downstream per-leg accounting (dust computation, refund-existence checks keyed by `order.inputs[i].token`, and destination-side output/`_partialFills` bucket collisions analogous to `testRevert_PlaceOrder_DuplicateOutputTokens`) unreliable, since the destination and any settlement logic assumes one distinct escrow slot per input leg but the Tron gateway silently folds duplicate legs into one bucket.

### Impact Explanation
This is Medium severity. It does not directly let an attacker mint funds out of thin air from a single order (unlike GMX's claimable-funding double-count, which directly doubles a claimable payout), but it breaks the invariant that `_orders[commitment][token]` corresponds 1:1 to a single order leg, which the withdrawal, refund, and cross-chain settlement paths (`withdraw()`, `cancelOrder()`, and the destination-side fill/`_partialFills` tracking mirrored from `IntrinsicIntents.sol`) rely on. Given the two existing regression tests in the sibling implementation explicitly describe "over-release" of escrow and "premature finalization" of duplicated legs as concrete exploitable consequences of this exact bug class, an attacker able to place orders with duplicate input/output token entries on the Tron gateway can manipulate escrow release/refund accounting to release more or less than intended, or desynchronize the fill-completion logic — a form of fund freezing/miscounting analogous to the GMX report.

### Likelihood Explanation
High reachability: `placeOrder` is a fully public, unprivileged entry point reachable by any user submitting a single transaction with a crafted `Order.inputs` array containing a repeated token address. No special privileges or multi-step setup are required, matching the "single submitted transaction" reachability bar.

### Recommendation
Port the same guard used in `evm/src/apps/IntentGatewayV2.sol` into `evm/tron/contracts/apps/IntentGatewayV2.sol`: replace the `+=` accumulation of `_orders[commitment][token]` in `placeOrder` with an assignment guarded by `if (_orders[commitment][token] != 0) revert InvalidInput();`, rejecting any order whose `inputs` array contains the same token address more than once. The equivalent duplicate-output-token check applied on the destination/fill side (as tested by `testRevert_PlaceOrder_DuplicateOutputTokens`) should also be verified as present in the Tron variant's fill/partial-fill logic.

### Proof of Concept
1. Construct an `Order` where `inputs[0].token == inputs[1].token == USDC` with `inputs[0].amount = A` and `inputs[1].amount = B`.
2. Call `IntentGatewayV2(tron).placeOrder(order, graffiti)`, approving USDC for `A+B`.
3. In the non-predispatch branch, both loop iterations execute `_orders[commitment][USDC] += reducedInputs[i].amount`, producing a single combined escrow slot `_orders[commitment][USDC] = reducedAmount(A) + reducedAmount(B)` — this collapses what should be two independently trackable legs into one, unlike `evm/src/apps/IntentGatewayV2.sol` where the second iteration would `revert InvalidInput()`.
4. Because downstream logic (`cancelOrder`'s per-input existence check at [5](#0-4) , and any output-side `_partialFills[commitment][outputToken]` accounting mirrored from `IntrinsicIntents.sol`) assumes one escrow/fill bucket per leg, an order deliberately crafted with duplicate token legs can desynchronize fill/refund accounting the same way the linked regression tests (`testRevert_PlaceOrder_DuplicateInputTokens`, `testRevert_PlaceOrder_DuplicateOutputTokens`) demonstrate for the main EVM contract before its fix was added.

### Citations

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

**File:** evm/tests/foundry/IntentGatewayV2SameChainTest.sol (L2115-2121)
```text
    /// @notice Placing an order with duplicate input tokens must revert.
    /// Regression test for: same-chain partial fills over-release repeated input escrow.
    function testRevert_PlaceOrder_DuplicateInputTokens() public {
        // Two input legs both using USDC — this previously merged into one escrow bucket
        TokenInfo[] memory inputs = new TokenInfo[](2);
        inputs[0] = TokenInfo({token: bytes32(uint256(uint160(address(usdc)))), amount: 1200 * 1e6});
        inputs[1] = TokenInfo({token: bytes32(uint256(uint160(address(usdc)))), amount: 1000 * 1e6});
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L437-469)
```text
                uint256 dust = balance - requiredAmount;
                if (dust > 0) emit DustCollected(token, dust);

                // Store reduced amount (after protocol fees) in escrow
                _orders[commitment][token] += reducedInputs[i].amount;

                unchecked {
                    ++i;
                }
            }

            // Execute transfer calls from call dispatcher
            ICallDispatcher(dispatcher).dispatch(abi.encode(transferCalls));
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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L548-557)
```text
            // Cross-chain: fetch storage proof
            uint256 inputsLen = order.inputs.length;
            for (uint256 i; i < inputsLen;) {
                // check for order existence
                if (_orders[commitment][address(uint160(uint256(order.inputs[i].token)))] == 0) revert UnknownOrder();

                unchecked {
                    ++i;
                }
            }
```
