### Title
Same-chain partial fill can round the released escrow to zero, letting a solver's real output payment return no input — ([File: evm/src/apps/intentsv2/IntrinsicIntents.sol])

### Summary
`_fillSameChain` computes the escrow released to a filling solver via a floor-division proportion, `escrowedAmount = (order.inputs[i].amount * fillAmount) / totalRequired`, with no check that this result is non-zero before transferring `fillAmount` of the solver's own output tokens to the beneficiary. This is the same bug class as the reported Perennial vault issue: a legitimate, non-zero contribution (`fillAmount > 0`, real tokens sent to `beneficiary`) can be rewarded with zero shares/escrow due to rounding down, causing an outright loss for the party providing value — here the solver instead of the depositor.

### Finding Description
In `_fillSameChain` [1](#0-0) , for a non-final partial fill (`amountFilled != totalRequired`), the escrowed input released to the solver is:

```solidity
escrowedAmount = (order.inputs[i].amount * fillAmount) / totalRequired;
```

This is a floor division with no minimum-fill-size or zero-result check. `fillAmount` is attacker/solver controlled (`solverAmount` from `FillOptions.outputs[i].amount`), and can be made deliberately small relative to `totalRequired` so that `order.inputs[i].amount * fillAmount < totalRequired`, making `escrowedAmount` truncate to `0`.

Before this computation, the solver has already unconditionally paid `beneficiaryTotal` (== `fillAmount`, since `beneficiaryShare` is 0 on a non-first partial fill) of its own output tokens to `beneficiary` via `safeTransferFrom`/native transfer [2](#0-1) . The function then proceeds to emit `PartialFill` and call `_withdraw` with an `escrowedInputs[i].amount == 0` entry, which is simply skipped by `_withdraw`'s `if (amount == 0) continue;` guard [3](#0-2) . `_partialFills[commitment][outputToken]` is nonetheless permanently advanced by `fillAmount` [4](#0-3) , so the solver's real payment is consumed against the order's remaining amount while it receives zero input tokens in return — a permanent, uncompensated transfer of value from the filling solver to the order's `beneficiary`.

This differs from the already-mitigated cumulative-dust issue covered by `testPartialFill_RoundingDustReleasedToFinalSolver` (Finding #4), which only ensures the *last* solver to complete an order receives the full remaining balance rather than a further-truncated slice [5](#0-4) . That fix does not address an *intermediate* fill whose single-shot proportional release rounds all the way down to zero — no test in the suite exercises `fillAmount` small enough, relative to `order.inputs[i].amount` and `totalRequired`, to produce `escrowedAmount == 0` on a non-final fill.

### Impact Explanation
Any unprivileged solver calling `fillOrder`/`_fillSameChain` on an order whose input/output ratio and remaining amount permit a fractional fill sized such that `(inputs[i].amount * fillAmount) / totalRequired == 0` loses the full value of that fill's output tokens for zero compensation — the tokens land at the order's `beneficiary` and the solver gets nothing back, while its "contribution" is silently marked as consumed progress toward the order (`_partialFills` incremented). This is a concrete, reachable fund-loss path from a single `fillOrder` transaction by any permissionless filler, satisfying the "concrete theft/permanent freezing of funds" bar: the value is not frozen so much as unconditionally transferred away from the solver with no recourse (the order can even reach `isFullyFilled` with the solver never getting the shortfall back, and there's no operation that lets the solver reclaim the zero-valued proportional share later). It also lets a griefer (or the `beneficiary` colluding with themselves as a "solver") drain a solver's tokens for orders with unfavorable input/output decimal ratios, or lets any filler unintentionally get a raw deal on dust-sized partial fills of large orders with small input amounts.

### Likelihood Explanation
Likelihood is Medium: it requires input/output decimals or amounts to align such that a legitimate partial-fill size produces less than one unit of input for a unit fill of output (e.g., an order with a low-decimal or small `inputs[i].amount` relative to a high-decimal, large `totalRequired`, or a filler intentionally choosing a very small `fillAmount`). Since `fillAmount` is fully attacker-controlled per-call and the check is a strict `> 0` on `remaining`/`solverAmount` only (not on the derived `escrowedAmount`), triggering it requires no special privilege and no race — it is deterministic given the order's parameters.

### Recommendation
Revert `_fillSameChain` when the computed `escrowedAmount` for a non-final fill would be zero while `fillAmount > 0` (mirroring the `_convertToShares` zero-shares check recommended in the reference report), e.g.:

```solidity
} else {
    escrowedAmount = (order.inputs[i].amount * fillAmount) / totalRequired;
    if (escrowedAmount == 0) revert InvalidInput(); // or a dedicated ZeroEscrowRelease error
}
```

Alternatively, enforce a protocol-level minimum `fillAmount` per output token proportional to `totalRequired`/`order.inputs[i].amount` so that no non-final partial fill can round to a zero release, and document/test the boundary explicitly the way the existing `testPartialFill_RoundingDustReleasedToFinalSolver` tests document the final-fill dust case.

### Proof of Concept
Given an order with `order.inputs[i].amount = 1` (e.g., 1 wei of a low-decimal input token) and `totalRequired = 1_000_000` (output units), a solver calling `fillOrder` with `solverAmount = 500_000` (a legitimate 50% partial fill, `alreadyFilled == 0`, not first-fill overpay) causes:
- `fillAmount = 500_000`
- solver transfers `500_000` of the output token to `beneficiary` (real payment, `IERC20.safeTransferFrom`/native transfer executes unconditionally) [6](#0-5) 
- `escrowedAmount = (1 * 500_000) / 1_000_000 = 0` [7](#0-6) 
- `_withdraw` skips the zero-amount token transfer [3](#0-2) , so the solver receives 0 input tokens
- `_partialFills[commitment][outputToken]` is nonetheless updated to `500_000`, permanently recording the fill as progress

The solver has paid 500,000 units of output token and received nothing, with no revert or safeguard anywhere in the call path.

### Citations

**File:** evm/src/apps/intentsv2/IntrinsicIntents.sol (L91-106)
```text
            uint256 amountFilled = alreadyFilled + fillAmount;
            _partialFills[commitment][outputToken] = amountFilled;
            uint256 beneficiaryTotal = fillAmount + beneficiaryShare;

            if (token == address(0)) {
                if (msgValue < beneficiaryTotal + protocolShare) revert InsufficientNativeToken();
                msgValue -= (beneficiaryTotal + protocolShare);
                // Inline, not `_sendValue`: this loop is at the via-ir stack limit.
                (bool sent,) = beneficiary.call{value: beneficiaryTotal}("");
                if (!sent) revert InsufficientNativeToken();
            } else {
                IERC20(token).safeTransferFrom(msg.sender, beneficiary, beneficiaryTotal);
                if (protocolShare > 0) {
                    IERC20(token).safeTransferFrom(msg.sender, address(this), protocolShare);
                }
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

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L456-459)
```text
        for (uint256 i; i < len; i++) {
            address token = address(uint160(uint256(body.tokens[i].token)));
            uint256 amount = body.tokens[i].amount;
            if (amount == 0) continue;
```

**File:** evm/tests/foundry/IntentGatewayV2SameChainTest.sol (L1727-1841)
```text
    /*//////////////////////////////////////////////////////////////
                    ROUNDING DUST IN PARTIAL FILLS (Finding #4)
    //////////////////////////////////////////////////////////////*/

    /// @notice Verifies that rounding dust from integer division in partial fills
    /// is not permanently locked. The final solver completing the order should
    /// receive the full remaining escrow balance rather than a truncated amount.
    function testPartialFill_RoundingDustReleasedToFinalSolver() public {
        // Choose amounts that produce rounding truncation:
        // input = 100 USDC (100e6), output = 3 DAI (3e18)
        // Each of 3 solvers fills 1 DAI. Proportional release per fill:
        //   100e6 * 1e18 / 3e18 = 33333333 (truncated from 33333333.33...)
        // Without fix: 3 * 33333333 = 99999999, leaving 1 unit locked.
        // With fix: final solver gets remaining balance = 100e6 - 2*33333333 = 33333334
        uint256 inputAmount = 100 * 1e6; // 100 USDC
        uint256 outputAmount = 3 * 1e18; // 3 DAI

        TokenInfo[] memory inputs = new TokenInfo[](1);
        inputs[0] = TokenInfo({token: bytes32(uint256(uint160(address(usdc)))), amount: inputAmount});

        TokenInfo[] memory outputAssets = new TokenInfo[](1);
        outputAssets[0] = TokenInfo({token: bytes32(uint256(uint160(address(dai)))), amount: outputAmount});

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

        // User places order
        vm.startPrank(user);
        usdc.approve(address(intentGateway), inputAmount);
        intentGateway.placeOrder(order, bytes32(0));
        vm.stopPrank();

        order.user = bytes32(uint256(uint160(user)));
        order.source = host.host();
        order.nonce = 0;

        uint256 fillPerSolver = 1e18; // Each solver fills 1 DAI
        uint256 truncatedRelease = (inputAmount * fillPerSolver) / outputAmount; // 33333333

        // --- Solver 1 fills 1 DAI ---
        address solver1 = makeCleanAddr("solver1");
        vm.deal(solver1, 1 ether);
        deal(address(dai), solver1, 10 * 1e18);
        uint256 solver1UsdcBefore = usdc.balanceOf(solver1);

        vm.startPrank(solver1);
        dai.approve(address(intentGateway), fillPerSolver);
        TokenInfo[] memory out1 = new TokenInfo[](1);
        out1[0] = TokenInfo({token: bytes32(uint256(uint160(address(dai)))), amount: fillPerSolver});
        intentGateway.fillOrder(order, FillOptions({relayerFee: 0, nativeDispatchFee: 0, validUntil: 0, outputs: out1}));
        vm.stopPrank();

        assertEq(
            usdc.balanceOf(solver1),
            solver1UsdcBefore + truncatedRelease,
            "Solver1 should receive truncated proportional USDC"
        );

        // --- Solver 2 fills 1 DAI ---
        address solver2 = makeCleanAddr("solver2");
        vm.deal(solver2, 1 ether);
        deal(address(dai), solver2, 10 * 1e18);
        uint256 solver2UsdcBefore = usdc.balanceOf(solver2);

        vm.startPrank(solver2);
        dai.approve(address(intentGateway), fillPerSolver);
        TokenInfo[] memory out2 = new TokenInfo[](1);
        out2[0] = TokenInfo({token: bytes32(uint256(uint160(address(dai)))), amount: fillPerSolver});
        intentGateway.fillOrder(order, FillOptions({relayerFee: 0, nativeDispatchFee: 0, validUntil: 0, outputs: out2}));
        vm.stopPrank();

        assertEq(
            usdc.balanceOf(solver2),
            solver2UsdcBefore + truncatedRelease,
            "Solver2 should receive truncated proportional USDC"
        );

        // --- Solver 3 fills final 1 DAI (completes the order) ---
        address solver3 = makeCleanAddr("solver3");
        vm.deal(solver3, 1 ether);
        deal(address(dai), solver3, 10 * 1e18);
        uint256 solver3UsdcBefore = usdc.balanceOf(solver3);

        vm.startPrank(solver3);
        dai.approve(address(intentGateway), fillPerSolver);
        TokenInfo[] memory out3 = new TokenInfo[](1);
        out3[0] = TokenInfo({token: bytes32(uint256(uint160(address(dai)))), amount: fillPerSolver});
        intentGateway.fillOrder(order, FillOptions({relayerFee: 0, nativeDispatchFee: 0, validUntil: 0, outputs: out3}));
        vm.stopPrank();

        // Final solver should receive the remaining balance (truncatedRelease + 1 rounding unit)
        uint256 expectedFinalRelease = inputAmount - (2 * truncatedRelease); // 33333334
        assertEq(
            usdc.balanceOf(solver3),
            solver3UsdcBefore + expectedFinalRelease,
            "Final solver should receive remaining escrow including rounding dust"
        );
        assertGt(expectedFinalRelease, truncatedRelease, "Final release should be larger due to rounding dust");

        // Gateway should have zero USDC — no dust locked
        assertEq(usdc.balanceOf(address(intentGateway)), 0, "Gateway should have zero USDC - no rounding dust locked");
    }
```
