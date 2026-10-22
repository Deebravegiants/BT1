# [M] M-02 | Errant Origination Fee Validation

## Summary
Severity: Medium
Contest weight: 0.0462
Dataset id: 20863
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The contract contains a logic error in the function that sets the loan origination fee. The business rule requires the fee to be capped at ten percent of the loan amount, which corresponds to a maximum of 1,000 basis points. However, the implementation validates the supplied fee by asserting that it is less than 10,000 basis points, a limit that actually represents one hundred percent. Because the comparison uses the wrong constant, any fee value up to 9,999 basis points (approximately 99.99%) passes the check. This mistake originates from an off‑by‑order‑of‑magnitude validation, where the intended upper bound was mistakenly multiplied by ten. An attacker who can invoke the fee‑setting function—typically an admin or a compromised privileged account—can therefore set an exorbitant origination fee. When a borrower requests a loan, the contract deducts the configured fee from the disbursed amount; with a fee near 100 % the borrower receives only a tiny fraction of the expected funds, effectively losing the majority of the loan value. From the user’s perspective the UI may display a reasonable percentage (e.g., “10 %”) or simply show the fee amount, but the underlying contract permits a far higher fee, leading to unexpected zero or near‑zero balances after borrowing. The impact is financial loss for borrowers, erosion of trust in the protocol, and potential reputational damage. The issue was uncovered during a manual audit that compared the documented fee cap with the actual Solidity require statement and identified the mismatched constant. Because the bug resides in a single comparison, it may not be obvious during normal operation unless a fee is deliberately set to an extreme value, making it easy to overlook in testing. The proper remediation is to adjust the validation to enforce that the fee is strictly less than 1,000 basis points (or equal to 1,000 if the policy allows exactly ten percent) and to ensure that any future changes to fee limits are reflected consistently across documentation, UI, and contract checks. Adding comprehensive unit tests that verify the fee cannot exceed ten percent and reviewing access control for the fee‑setting function further mitigates the risk.

## Recommendation
Validate that the _loanOriginationFee value is less than 1_000, rather than less than 10_000.
