# [M] M-05 | Settlement Price frontrunning

## Summary
Severity: Medium
Contest weight: 0.0956
Dataset id: 22088
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Any user can grief the protocol by frontrunning the submitSettlementPrice function call and asserting a price directly to UMA. UMA determines the assertion ID by taking in the following parameters: assertionId = _getId(claim, bond, time, liveness, currency, callbackRecipient, escalationManager, identifier); All of which an attacker can copy what Foil was going to use. When the attacker's transaction gets executed first, Foil's will revert shortly after with the following check: require(assertions[assertionId].asserter == address(0), "Assertion already exists");

## Recommendation
Since time is one of the parameters to create an assertion, submitting the transaction through a private mem-pool will be sufficient to prevent this attack.
