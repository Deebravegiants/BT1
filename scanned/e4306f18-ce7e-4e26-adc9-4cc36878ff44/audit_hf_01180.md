# [H] Incorrect Curve Cap Comparison May Allow Overflow Beyond Curve Terminal

## Summary
Severity: High
Contest weight: 0.6444
Dataset id: 5057
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the Agent contract, the following check is used to prevent trades from exceeding the maximum supply bound of the bonding curve:  
```solidity
require(
    scaledTokensSoldPercentage + scaledNewTokensPercentage < CURVE_DENOMINATOR * PRECISION,
    "Purchase exceeds bonding curve limit"
);
```  
This logic is flawed. The bonding curve is designed to terminate at 100% token supply usage, which should be checked using 1 * PRECISION (or just PRECISION for short) rather than CURVE_DENOMINATOR * PRECISION. CURVE_DENOMINATOR is a scaling constant used in the pricing formula but does not represent a true 100% bound in normalized units. Using it in this context falsely enlarges the permitted trade window.  
As a result, the contract may allow purchases that exceed the full curve allocation, resulting in attempted overdraws from the contract's token balance. While such a purchase will often fail due to a transfer or balance check downstream, the check is not tight enough to enforce the curve’s terminal condition at the level of logic enforcement.  
An additional nuance is that the inequality used is <, which prohibits reaching exactly the end of the curve (100%). This inadvertently protects against the exploit scenario described in the bonding curve asymptotic mispricing issue. However, if the condition is ever changed to <= for design reasons, and the limit remains incorrectly set to CURVE_DENOMINATOR * PRECISION, then an attacker could reach the end, trigger mispricing logic (e.g., artificially low endPrice), and underpay for tokens.  
In cases where the contract receives unexpected token donations (e.g., via direct transfer bypassing logic), the balance would be artificially increased, allowing buys that exceed the curve supply constraint without triggering reverts, further exacerbating the issue.

Impact Explanation:  
Medium, because although token transfers will often fail when attempting to exceed the curve bounds, the invalid check opens a window for economic manipulation and logical inconsistencies. In some edge cases (e.g., external token donation or LP delay), attackers may exploit the mispricing near the curve end.

## Recommendation
Replace the comparison constant with an explicit cap of 1 * PRECISION (or just PRECISION for short) to accurately represent the full curve limit. This ensures no purchase is allowed once the full curve allocation is reached, enforcing proper economic constraints and protecting against overflow or rounding errors. The inequality direction (< vs <=) should also be reviewed to ensure it matches intended bonding curve semantics at the terminal supply.
