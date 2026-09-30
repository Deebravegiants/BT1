# [H] H-05 | Users Tricked To Match Withdrawals

## Summary
Severity: High
Contest weight: 0.2008
Dataset id: 2041
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Stakers can opt to exit the vault by creating a withdrawal request that can be matched by other users, incentivizing them with a donation amount. Malicious users can trick matchers to accept their orders by creating a high donation amount compared to the request amount. By front-running the ExitVault.matchWithdrawRequest, they can invalidate their request and create a new request with a higher amount causing the donationPart calculation to drastically drop. Consider this scenario: • userA creates a withdrawal request: amount = 10 donation = 5 • userB sends a tx to match the request, _fillAmount = 5 _minDonation=5 = (should receive 5 in donation) • userA frontruns the tx, invalidates request and creates a new one: amount = 100 donation=5 • userB now receives 5 * 5 / (100-5) = 0.26

## Recommendation
Validate the _minDonation amount against the donationPart instead of the request.donation.
