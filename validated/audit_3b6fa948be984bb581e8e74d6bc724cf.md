Based on my investigation, I found a genuine analog to the AbstractRewarder precision-loss report within Hyperbridge's intents infrastructure: proportional escrow release in `IntentGatewayV2`/`IntentsBase` uses integer division for partial fills, which truncates and can strand dust in escrow.

### Title
Integer-division truncation in partial-fill escrow release can permanently strand dust in `IntentsBase`/`IntentGatewayV2` escrow - (File: evm/src/apps/intentsv2/IntentsBase.sol, evm/src/apps/IntentGatewayV2.sol)

### Summary
The reported bug class is precision loss from integer division that is never reconciled, leaving funds permanently stuck in a contract with no recovery path. The same class of bug exists in Hyperbridge's cross-chain intents settlement: a solver's proportional escrow release for a partial fill is computed as `input.amount * fillAmount / totalRequired`, an integer division that truncates downward on every partial fill.

### Finding Description
When a solver partially fills a cross-chain order, the released portion of the user's escrowed input is calculated proportionally to how much output was delivered relative to the total required output, e.g. `(input.amount * output.amount) / requested` [1](#0-0) . This mirrors exactly the `rewardPerToken`/`earned()` pattern in the external report: a proportional share computed via `numerator / denominator` with the numerator's multiplication happening before division, so any fractional remainder is discarded rather than carried forward.

A dedicated regression test, `testPartialFill_RoundingDustReleasedToFinalSolver`, documents the exact failure mode: for `inputAmount = 100e6`, `outputAmount = 3e18`, three sequential 1-DAI partial fills each release `33333333` units (truncated from `33333333.33...`), and without a fix, `3 * 33333333 = 99999999`, leaving `1` unit of USDC permanently locked in escrow instead of the full `100e6` [2](#0-1) . This is functionally identical to the audit report's Scenario 1/2: repeated proportional divisions each drop a fractional remainder, and the residual accumulates as unrecoverable dust inside the contract, exactly like AbstractRewarder's stuck reward tokens.

Similarly, the same-chain fill path computes protocol fees via `(originalAmount * protocolFeeBps) / 10_000` and surplus splits via `(dust * surplusShareBps) / 10_000`, both truncating divisions whose remainders are explicitly tracked as `DustCollected` events rather than reconciled [3](#0-2) [4](#0-3) . Unlike the reward-per-token case, here the dust is emitted as an event and appears intentionally routed to the protocol as "DustCollected," which suggests the protocol-fee and surplus paths already treat truncation as by-design revenue rather than a bug. However, the partial-fill proportional-release path (the one covered by `testPartialFill_RoundingDustReleasedToFinalSolver`) is different: that dust is not attributed anywhere — the test's own comment states the fix requires giving "the final solver ... the full remaining escrow balance rather than a truncated amount" [5](#0-4) .

I was unable to locate the actual current implementation of the partial-fill release logic (the function computing `releasedInput`/`totalRequired`/`fillAmount` in the production contract) within the indexed codebase — my searches for `totalRequired`, `fillAmount`, `releasedInput`, and `amountFilled` inside `IntentsBase.sol` and `IntentGatewayV2.sol` returned no hits, only in `IntrinsicIntents.sol` comments referencing that logic and in the Foundry test file. This means I could not confirm from the indexed content whether the fix described in the test (crediting the final solver with the full remaining balance) is actually implemented in the current production contract, or whether the test exists to guard against a regression of an already-fixed issue.

### Impact Explanation
If the truncation is not fully reconciled on the final partial fill (i.e., if the last solver to complete an order receives only the proportionally truncated amount rather than the full remaining escrow balance), then per-order dust equal to a few base units of the input token becomes permanently locked in the `IntentGatewayV2`/`IntentsBase` escrow with no withdrawal mechanism — the same "irrecoverable funds" impact class as the original report. Because Hyperbridge's intents system processes many orders across many chains, this dust would accumulate over time analogous to how AbstractRewarder's reward-rate truncation accumulates "over a year or two."

### Likelihood Explanation
Medium. The codebase itself has already written a specific regression test targeting this exact scenario (`testPartialFill_RoundingDustReleasedToFinalSolver`, "Finding #4"), which strongly suggests this was previously identified as a real issue and a fix (crediting the final solver with the full remaining balance) was intended/applied. Whether that fix is present and correct in the currently deployed contract could not be verified from the available indexed contract source — the actual escrow-release function body was not retrievable via search, so I cannot confirm whether the vulnerability is still live or has already been remediated.

### Recommendation
Verify (via a live Devin session with full repository access, since the index does not surface the relevant function body) that the partial-fill escrow-release logic in `IntentsBase.sol`/`IntentGatewayV2.sol` credits the *final* fill of an order with the full remaining escrowed balance rather than a proportionally truncated amount, exactly as the existing test `testPartialFill_RoundingDustReleasedToFinalSolver` asserts. If any code path still computes every fill (including the last) via truncating division without a final-fill reconciliation step, add one so escrow can never retain unrecoverable dust.

### Proof of Concept
The existing test in the repository already demonstrates the failure mode and expected fix: [2](#0-1)

### Citations

**File:** evm/tests/foundry/IntentGatewayV2SameChainTest.sol (L1731-1741)
```text
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
```

**File:** evm/src/apps/IntentGatewayV2.sol (L340-352)
```text
        if (protocolFeeBps > 0) {
            reducedInputs = new TokenInfo[](inputsLen);
            for (uint256 i; i < inputsLen;) {
                uint256 originalAmount = order.inputs[i].amount;
                if (originalAmount == 0) revert InvalidInput();
                uint256 protocolFee = (originalAmount * protocolFeeBps) / 10_000;
                uint256 reducedAmount = originalAmount - protocolFee;
                address token = address(uint160(uint256(order.inputs[i].token)));

                if (protocolFee > 0) emit DustCollected(token, protocolFee);

                reducedInputs[i] = TokenInfo({token: order.inputs[i].token, amount: reducedAmount});
                unchecked {
```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L426-434)
```text
    function _splitSurplus(uint256 dust, bool hasOutputCall)
        internal
        view
        returns (uint256 protocolShare, uint256 beneficiaryShare)
    {
        if (hasOutputCall) return (dust, 0);
        protocolShare = (dust * _params.surplusShareBps) / 10_000;
        beneficiaryShare = dust - protocolShare;
    }
```
