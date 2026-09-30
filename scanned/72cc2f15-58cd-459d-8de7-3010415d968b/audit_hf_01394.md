# [M] Centralization Risks

## Summary
Severity: Medium
Contest weight: 0.1054
Dataset id: 7133
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the current implementation setup, the owner is meant to be a single Externally Owned Account
(EOA) which could potentially introduce security risks regarding single points of failure or misman-
agement.
One possible attack scenario is if the owner is compromised a DoS attack on the protocol can be
executed based on pausing functionality.
Additionally the following functions: updateWhitelistClaimAllocations(), provideSupply(),
setRoyaltyReceiver(), addManagerContract(), removeManagerContract() are dependant solely
on the owner and a single mistake can lead to serious impact.

## Recommendation
It’s crucial for the long-term success and trustworthiness of the project to address these concerns
thoroughly. One possible solution is using a multi-sig or governance as the protocol owner. Addition-
ally consider using a Timelock smart contract so that users know in advance the applied changes.
