# [M] Duplicated Mint Requests May Be Confirmed

## Summary
Severity: Medium
Contest weight: 0.1379
Dataset id: 14741
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
There are no requirements in the contracts that prevent a Merchant from successfully calling Factory.addMintRequest() multiple times for the same deposit. It is also possible for the Issuer to subsequently confirm the duplicated requests.
Two identical calls can be made by a Merchant to addMintRequest(), which are both accepted. The values of nonce will differ between the requests, and so will requestHash. The parameter txid is not used for validation, so there is nothing in the contracts to ensure the requests refer to separate transactions.
For the same reason, a Merchant may also call Factory.addMintRequest() to create new mint requests for previously rejected or cancelled mint requests.
The system therefore relies on the validators to pick up duplicate mint requests to prevent tokens being minted twice in these situations.

## Recommendation
The protocol could be changed to require txid to be used, although this is a significant design change.
Alternatively, if the team wishes to keep the current design, they should remain keenly aware of this issue and be sure that the Issuer validators have a robust system to avoid minting AMKT from duplicate requests.
