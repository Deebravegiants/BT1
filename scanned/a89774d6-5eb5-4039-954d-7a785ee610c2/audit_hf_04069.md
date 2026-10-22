# [C] AV-1 | Request Can Be Cancelled For Other Asset Vault

## Summary
Severity: Critical
Contest weight: 0.2245
Dataset id: 20522
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When a user cancels their request with the function cancelRequest, it is verified that the user cancelling the request is indeed the sender who sent the request. Afterwards, the funds contained in the Asset Vault are sent to the user depending on the amount of the request. However, there is no validation done to ensure that a user who deposited/redeemed into one Asset Vault is not cancelling the created request on the other Vault.

For example, for illustrative purposes, consider the drastic scenario of a user creating a 1 ether deposit into the ETH Vault. The user can then trivially call cancelRequest on the USDC Vault, and be refunded 1e18 USDC. This leads to an enormous loss of funds for the USDC Vault depositors which is extremely easy to perform.

## Proof of Concept
https://github.com/GuardianAudits/UmamiPoCs/commit/f4c86b33be7f298296d2b1a485be946074edcfca

## Recommendation
Use the vault attribute of the OCRequest to ensure that cancellation is only performed for the Asset Vault in which the deposit/redeem was intended.
