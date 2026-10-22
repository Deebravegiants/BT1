# [M] M-7 Assets may be unexpectedly seized

## Summary
Severity: Medium
Contest weight: 0.0347
Dataset id: 7331
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
During the liquidation process of the lending protocol, a borrower’s assets can be taken even if the borrower never listed those assets as collateral through the enterMarket function. The root cause is that the liquidation routine does not verify that each seized token is part of the borrower’s explicitly entered collateral markets. As a result, when a liquidator calls the liquidation function, the contract may arbitrarily select any token balance held by the borrower and transfer it to the liquidator. This can be exploited by an attacker who identifies a borrower with a non‑zero balance of a token that was never entered as collateral, triggers a liquidation on the borrower’s outstanding debt, and then receives the unrelated token as part of the seized collateral. The impact is that borrowers lose assets they never intended to risk; from the user’s perspective the balance of an unrelated token may drop to zero or shrink unexpectedly after a liquidation event, violating the expectation that only declared collateral is at risk. The condition under which this occurs is any liquidation call where the protocol’s seize logic is invoked without a prior check against the borrower’s entered markets. All borrowers who hold tokens not entered as collateral are potentially affected, and the protocol’s reputation and financial integrity are compromised because accounting assumptions about collateral coverage are broken. The issue was discovered during a manual security audit that examined the liquidation flow and noticed the missing whitelist verification. It is hard to notice because typical test suites only validate that declared collateral can be seized, overlooking the possibility that the contract may accept any token balance. To remediate, the protocol should enforce a check that only assets explicitly listed by the borrower via enterMarket are eligible for seizure, rejecting any attempt to seize non‑entered assets. This change restores the intended business logic that collateral risk is limited to user‑approved markets and prevents unexpected asset loss.

## Recommendation
We recommend prohibiting the seizure of assets that are not explicitly listed by the borrower as allowed collateral through enterMarket.
