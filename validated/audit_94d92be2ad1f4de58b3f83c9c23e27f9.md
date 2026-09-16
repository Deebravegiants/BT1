### Title
Same-chain partial-fill escrow release rounds down to zero, letting order creators drain solver output tokens for free - (File: `evm/src/apps/intentsv2/IntrinsicIntents.sol`)

### Summary
`_fillSameChain` computes the proportional amount of escrowed input tokens to release to a solver on a *partial* fill using floor division. When the ratio of escrowed input to requested output is small enough, a legitimate partial fill releases `0` escrowed tokens to the solver even though the solver has already transferred real output tokens to the beneficiary, exactly mirroring the Sherlock H-01 rounding bug (`collateralReward` rounding to 0 in `Pool.sol`).

### Finding Description
In `_fillSameChain`, for a fill that does not complete the order, the escrowed input released to the solver is: [1](#0-0) 

```solidity
uint256 escrowedAmount;
if (amountFilled == totalRequired) {
    escrowedAmount = _orders[commitment][address(uint160(uint256(order.inputs[i].token)))];
} else {
    escrowedAmount = (order.inputs[i].amount * fillAmount) / totalRequired;
}
```

`order.inputs[i].amount` and `totalRequired` (`order.output.assets[i].amount`) are both set by the order creator (`order.user`) in `placeOrder`, while `fillAmount` is chosen by the filling solver. Because Solidity integer division truncates, whenever
`order.inputs[i].amount * fillAmount < totalRequired`, `escrowedAmount` rounds down to `0`.

Before reaching this branch, the solver has already unconditionally transferred `fillAmount` (plus any surplus share) of the output token to the beneficiary: [2](#0-1) 

So a solver who fills less than the full order (any fill that does not exactly complete the order in that same call) can transfer output tokens to the beneficiary and receive `0` escrowed input tokens back. The token amounts are fully attacker-controllable at order-creation time: a user can set a very small `order.inputs[i].amount` (e.g. a low-decimal token, small quantity) against a large `totalRequired` (e.g. an 18-decimal token requested in bulk), so that essentially any non-completing partial fill by an honest solver lands in the zero-rounding regime. This is directly analogous to the referenced report's `collateralReward = _amount * userInvertedCollateralRatioMantissa / 1e18` rounding to 0 when the ratio is skewed.

The mirrored cross-chain path, `ExtrinsicIntents.sol`, is not affected the same way because it requires `solverAmount >= totalRequired` for cross-chain fills (no partial fills), but the same-chain `_fillSameChain` path explicitly supports partial fills and is reachable by any unprivileged solver calling `fillOrder`.

### Impact Explanation
This is a concrete loss-of-funds vector reachable by any solver interacting with `fillOrder` for a same-chain order: a solver that performs a non-final partial fill on a maliciously (or even innocently) skewed order can send real output tokens to the beneficiary while the escrow-release logic returns `0` of the corresponding escrowed input. The order creator effectively receives output tokens for free at the solver's expense whenever the fill doesn't perfectly divide/complete the order. Since `_fillSameChain` is the core partial-fill accounting path of `IntentGatewayV2`, this can be triggered deterministically by any order combining a small input amount with a disproportionately large output amount — a real fund-loss condition, not merely a dust/rounding inefficiency (the existing "final solver gets remainder" fix only prevents residual dust from being *permanently locked in the contract*; it does nothing to protect an intermediate partial-filling solver whose single fill rounds to exactly zero).

### Likelihood Explanation
Likelihood is high: order parameters (`inputs[i].amount`, `output.assets[i].amount`) are fully controlled by the order creator, and any decimals mismatch or deliberately chosen ratio (e.g., low-decimal escrow token vs. high-decimal/large-quantity requested output) creates a wide range of `fillAmount` values for which `escrowedAmount` rounds to `0`. No special privileges, governance, or unusual chain conditions are required — only a normal `placeOrder` + `fillOrder` sequence with values chosen so `order.inputs[i].amount * fillAmount < totalRequired`.

### Recommendation
- Round the escrow-release amount up (ceiling division) rather than down, or track cumulative escrow already released and release the remainder proportionally so the last unit is never dropped for the solver.
- Alternatively, revert the fill (`InvalidInput`) when the computed `escrowedAmount` for a non-completing partial fill would be `0`, forcing the solver to either complete the order or choose a `fillAmount` large enough to receive non-zero escrow.
- Add an invariant test asserting that the sum of all `escrowedAmount` releases (including partials) always equals `order.inputs[i].amount` and that no individual non-final partial fill can legitimately release `0` while transferring a non-zero `fillAmount` of output tokens.

### Proof of Concept
1. `user` places an order with `inputs = [{token: USDC, amount: 100e6}]` (100 USDC, 6 decimals) and `output.assets = [{token: DAI, amount: 3e18}]` (i.e., requests 3 DAI, 18 decimals) — see the existing rounding scenario constants in [3](#0-2) .
2. A `solver` calls `fillOrder` with `outputs[0].amount = 1` (1 wei of DAI, a valid non-completing partial fill since `remaining = 3e18 > 1`).
3. In `_fillSameChain`, the solver's `fillAmount = 1` is transferred to `beneficiary` at line 102 (`IERC20(token).safeTransferFrom(msg.sender, beneficiary, beneficiaryTotal)`).
4. `escrowedAmount = (100e6 * 1) / 3e18 = 0` (line 115), so the solver receives `0` USDC in return for the DAI they just paid.
5. Repeating this with slightly larger, but still sub-threshold, `fillAmount` values (`fillAmount < totalRequired / order.inputs[i].amount`, i.e. `< 3e18/100e6 = 3e10`) continues to yield `escrowedAmount = 0`, letting the beneficiary accumulate output tokens from any solver operating in that range without paying anything back.

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

**File:** evm/src/apps/intentsv2/IntrinsicIntents.sol (L111-116)
```text
            uint256 escrowedAmount;
            if (amountFilled == totalRequired) {
                escrowedAmount = _orders[commitment][address(uint160(uint256(order.inputs[i].token)))];
            } else {
                escrowedAmount = (order.inputs[i].amount * fillAmount) / totalRequired;
            }
```

**File:** evm/tests/foundry/IntentGatewayV2SameChainTest.sol (L1734-1743)
```text
    function testPartialFill_RoundingDustReleasedToFinalSolver() public {
        // Choose amounts that produce rounding truncation:
        // input = 100 USDC (100e6), output = 3 DAI (3e18)
        // Each of 3 solvers fills 1 DAI. Proportional release per fill:
        //   100e6 * 1e18 / 3e18 = 33333333 (truncated from 33333333.33...)
        // Without fix: 3 * 33333333 = 99999999, leaving 1 unit locked.
        // With fix: final solver gets remaining balance = 100e6 - 2*33333333 = 33333334
        uint256 inputAmount = 100 * 1e6; // 100 USDC
        uint256 outputAmount = 3 * 1e18; // 3 DAI

```
