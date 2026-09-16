### Title
Duplicate input tokens silently merge into one escrow bucket in Tron's IntentGatewayV2 — bypassing the on EVM patched `InvalidInput` rejection - ([File: evm/tron/contracts/apps/IntentGatewayV2.sol])

### Summary
The mainline EVM `IntentGatewayV2.sol` / `IntentsBase.sol` rejects orders that declare duplicate input tokens (`if (_orders[commitment][token] != 0) revert InvalidInput();`) precisely because two separate escrow legs merged into a single accounting bucket previously caused an over-release of escrow on partial fills. The Tron fork (`evm/tron/contracts/apps/IntentGatewayV2.sol`) reintroduces exactly the un-fixed pattern: it accumulates into the bucket with `+=` and performs no duplicate-token check, so the vulnerability the mainline codebase explicitly regression-tested against is live on Tron deployments.

### Finding Description
This is the same bug class as the `_merge_positions()` report: a data structure meant to track two logically distinct quantities (per-input-token escrow legs there / per-input-token escrow amounts here) is merged/accumulated without the compensating logic that keeps downstream accounting consistent.

In `placeOrder`, Tron's `IntentGatewayV2.sol` escrows each input leg with: [1](#0-0) 
and, in the predispatch branch: [2](#0-1) 

Both branches write `_orders[commitment][token] += reducedInputs[i].amount;` with no check that `token` hasn't already been escrowed under this commitment. If `order.inputs` contains the same token twice (two legs, e.g. two USDC legs sized differently), both legs' amounts are folded into a single `_orders[commitment][token]` slot.

The mainline EVM contract fixed this exact defect: `placeOrder` now reverts with `InvalidInput` on a duplicate input token before escrow: [3](#0-2) 
and the regression test explicitly documents why: [4](#0-3) 
The comment "Two input legs both using USDC — this previously merged into one escrow bucket" together with the test name "Regression test for: same-chain partial fills over-release repeated input escrow" confirms the historical exploit path this same code pattern reproduces on Tron.

The downstream danger is in `IntrinsicIntents.sol`'s partial-fill accounting, which computes each leg's proportional escrow release independently, per leg index, assuming `order.inputs[i].amount` at index `i` maps to an isolated escrow bucket: [5](#0-4) 
and withdrawal drains the shared bucket by whatever amount a leg's calculation dictates: [6](#0-5) 
When two legs share one `_orders[commitment][token]` slot (because the Tron contract accumulated them together), a solver filling one leg can drain escrow amounts that were actually deposited for the *other* leg, since `_withdraw`/`_execute` operate on the merged total rather than two independently tracked amounts — an over-release of escrowed user funds to a solver, or a stuck/incorrect balance for legitimate withdrawal on order refund/cancel.

### Impact Explanation
This allows a user (attacker crafting their own order) or, more critically, a solver exploiting a maliciously/accidentally duplicated-token order, to obtain escrow release amounts larger than intended for one leg by drawing on funds nominally allocated to a second leg of the same token — a direct theft-of-funds / fund-freezing vector on the Tron-deployed IntentGateway. This matches the required "concrete theft or permanent freezing of funds" bar: escrowed user tokens can be over-released to a solver or become inconsistent with what the order's per-leg accounting expects, and the same duplicate-input-token order construction the EVM regression test proves exploitable is unguarded here.

### Likelihood Explanation
High. The attack requires only a single `placeOrder` call from any unprivileged user (identical to the EVM regression test's `testRevert_PlaceOrder_DuplicateInputTokens`) with two input legs referencing the same token address, followed by a normal `fillOrder`/partial-fill flow — the exact reachable path (single submitted transaction from an unprivileged actor) required by the analog scope. No admin, governance, or consensus compromise is needed; it is a pure application-logic bug already proven exploitable and regression-tested on the sibling EVM contract, but left unpatched in the Tron variant.

### Recommendation
Port the mainline fix to `evm/tron/contracts/apps/IntentGatewayV2.sol`: reject duplicate input tokens in `placeOrder` before escrowing (`if (_orders[commitment][token] != 0) revert InvalidInput();`) instead of accumulating with `+=`, mirroring `evm/src/apps/IntentGatewayV2.sol` lines 364-373, in both the predispatch and non-predispatch escrow loops. Add the same regression test (`testRevert_PlaceOrder_DuplicateInputTokens`) to the Tron test suite to prevent recurrence.

### Proof of Concept
1. Construct an `Order` with `inputs = [ {token: USDC, amount: 1200e6}, {token: USDC, amount: 1000e6} ]` and two output legs, exactly as in the existing EVM regression test (`evm/tests/foundry/IntentGatewayV2SameChainTest.sol:2117-2148`), but target Tron's `IntentGatewayV2.placeOrder`.
2. Because Tron's contract has no duplicate-token guard, both legs escrow into the same `_orders[commitment][USDC]` slot, totaling 2200e6 instead of being tracked as two independent 1200e6/1000e6 buckets.
3. A solver partially fills only the first output leg via `fillOrder`; `IntrinsicIntents._execute`/`_withdraw` computes the escrow release for leg 0 using `order.inputs[0].amount` (1200e6) against the merged, larger bucket, releasing/crediting an amount that does not correspond 1:1 to what was actually deposited for that specific leg, letting the solver capture value intended for leg 1's escrow or leaving leg 1's refund path inconsistent (freezing or misallocating funds) once the order is cancelled or the second leg is later filled.

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

**File:** evm/src/apps/intentsv2/IntrinsicIntents.sol (L111-118)
```text
            uint256 escrowedAmount;
            if (amountFilled == totalRequired) {
                escrowedAmount = _orders[commitment][address(uint160(uint256(order.inputs[i].token)))];
            } else {
                escrowedAmount = (order.inputs[i].amount * fillAmount) / totalRequired;
            }
            escrowedInputs[i] = TokenInfo({token: order.inputs[i].token, amount: escrowedAmount});
            outputFills[i] = TokenInfo({token: outputToken, amount: fillAmount});
```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L461-464)
```text
            uint256 escrowed = _orders[body.commitment][token];
            if (escrowed == 0) revert UnknownOrder();

            _orders[body.commitment][token] = escrowed - amount;
```
