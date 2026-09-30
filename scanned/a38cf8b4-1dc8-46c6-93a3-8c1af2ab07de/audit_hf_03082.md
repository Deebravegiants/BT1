# [M] Centralization risk of Feed contracts' VALIDATOR_ROLE

## Summary
Severity: Medium
Contest weight: 0.0798
Dataset id: 17406
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Any address that is granted the VALIDATOR_ROLE will bypass the aggregation and validator group signature process. DEFAULT_ADMIN_ROLE can be granted to any address by the admin of the FluxP2PFactory, and VALIDATOR_ROLE can be granted by addresses with the DEFAULT_ADMIN_ROLE. Any address that is given the VALIDATOR_ROLE can submit any answer to the price feed, thus bypassing the aggregation and validator group signature process. The price feed can be fed malicious answers.

## Recommendation
Consider simplifying the contract to make the transmit() function callable by the P2PFactory only.
