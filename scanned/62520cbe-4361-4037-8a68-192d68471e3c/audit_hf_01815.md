# [H] Wrong loop area

## Summary
Severity: High
Contest weight: 0.5222
Dataset id: 10074
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is a premature termination of a critical iteration loop that is intended to compute a formula until a residual value (delta) reaches zero. The loop’s exit condition is incorrectly placed, causing the iteration to stop before the delta variable is reduced to zero. As a result, the final computed value is based on an incomplete series of terms, leading to a systematic mis‑calculation of the protocol’s accounting logic. The root cause is a misplaced break or loop bound that does not reflect the intended number of tokens (numTokens_) and therefore fails to process the full set of inputs required for the formula. An attacker or any user invoking the affected function can exploit this by triggering the calculation with values that rely on the full loop execution; because the loop stops early, the returned amount may be lower than the correct entitlement, causing under‑payment, loss of expected rewards, or incorrect token minting. The impact is that users may receive fewer tokens than they are owed, balances can appear reduced or zero, and the protocol’s accounting invariants are broken, potentially leading to fund leakage or unfair distribution. This condition occurs whenever the function that contains the loop is called with a number of tokens greater than the hard‑coded limit or when the internal break condition is reached before delta reaches zero. All participants who rely on the accurate calculation—depositors, borrowers, liquidity providers—are affected because the protocol’s financial guarantees are compromised. The issue was discovered during a manual security review that compared the implementation against a reference calculation from a known correct contract (yETH) and observed that the loop stopped early. It is hard to notice because the contract may still return a value that looks plausible for small inputs, and the discrepancy only becomes evident with larger token sets or edge‑case parameters, making the bug subtle in normal testing. The proper fix is to move the arithmetic statements inside the loop so that they are executed for each token up to numTokens_, adjust the loop condition to iterate until the intended bound, and ensure that the delta variable is updated and checked after the loop completes. In conceptual terms, the bug belongs to the class of “incorrect loop termination” or “partial aggregation” errors, where a financial formula is not fully evaluated, violating the business logic that expects the sum of all token contributions to equal the total owed amount. From a user’s perspective the symptom is that a transaction that should credit a certain amount of tokens instead credits a smaller amount or even zero, contrary to the expectation of receiving the full calculated reward.

## Recommendation
These lines should be included in the loop only
```solidity
for (uint256 t = 0; t < MAX_NUM_TOKENS; t++) {
    if (t == numTokens_) break;
    _r = FixedPointMathLib.rawDiv(FixedPointMathLib.rawMul
    (_s, _sp), _s);
}
uint256 _delta = 0;
```
And change the following brackets accordingly.
