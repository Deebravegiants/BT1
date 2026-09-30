# [M] Contract Owner Can Arbitrarily Change Minting Fees and Interest Rates

## Summary
Severity: Medium
Contest weight: 0.0478
Dataset id: 14614
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability consists of a privileged parameter manipulation flaw in which the contract owner is able to modify the minting fee (issueFeeRate) and the interest rate (interestRate) after a loan has already been opened. The root cause is that the setter functions for these economic parameters are not restricted to a pre‑loan phase and are protected only by an owner‑only modifier, allowing the owner to change them at any time. An attacker who controls the owner address can exploit this by calling the fee‑adjustment functions after a borrower has taken a loan, raising the fee or interest to a level that equals or exceeds the collateral posted for that loan. When the borrower later attempts to repay or withdraw collateral, the contract will calculate a repayment amount that is dramatically higher than originally quoted, often consuming the entire collateral or causing the transaction to revert due to insufficient funds. The impact is that borrowers can lose the full value of their collateral, the protocol’s economic assumptions are broken, and user trust is eroded because the fee structure is no longer predictable. This condition occurs whenever a loan is active and the owner decides to change the parameters, affecting any user who has taken a loan, as well as the overall health of the lending platform. The issue was discovered during a manual audit that examined the mutability of economic variables and identified that the owner could invoke the setters after loan creation. It can be hard to notice because the contract’s UI may display the current fee rates without indicating that they can change retroactively, and the increased cost only becomes apparent at repayment time. To remediate, the minting fee should be made immutable after deployment or locked once the first loan is issued, and any changes to the interest rate should be governed by a multi‑signature or time‑locked mechanism rather than a single owner. This class of bug is commonly referred to as a privileged parameter change or mutable economic parameter vulnerability, which violates the business logic that fees should be fixed or at least predictable for the duration of a loan, leading to scenarios where funds disappear or refunds are unexpectedly reduced.

## Recommendation
While "dynamic" interest rates are common, we recommend considering the minting fee (issueFeeRate) to be a constant that cannot be changed by the owner.
