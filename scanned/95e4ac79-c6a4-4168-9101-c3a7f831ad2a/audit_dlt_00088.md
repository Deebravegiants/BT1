# [H] ASA-2024-0012, ASA-2024-0013: CosmosSDK: Transaction decoding may result in a stack overflow or resource exhaustion 

## Summary
Severity: High
Chain: Cosmos
Component: cosmos/cosmos-sdk
CWE: Uncontrolled Resource Consumption, Uncontrolled Recursion
Published: 2024-12-16
Source: https://github.com/cosmos/cosmos-sdk/security/advisories/GHSA-8wcc-m6j2-qxvm
Type: github-advisory

## Details
## Summary 

### ASA-2024-0012
Name: ASA-2024-0012,  Transaction decoding may result in a stack overflow
Component: Cosmos SDK
Criticality: High (Considerable Impact, and Possible Likelihood per [ACMv1.2](https://github.com/interchainio/security/blob/main/resources/CLASSIFICATION_MATRIX.md))
Affected versions: cosmos-sdk versions <= v0.50.10, <= v0.47.14
Affected users: Chain Builders + Maintainers, Validators, node operators

### ASA-2024-0013
Name: ASA-2024-0013: CosmosSDK: Transaction decoding may result in resource exhaustion  
Component: Cosmos SDK
Criticality: High (Considerable Impact, and Possible Likelihood per [ACMv1.2](https://github.com/interchainio/security/blob/main/resources/CLASSIFICATION_MATRIX.md))
Affected versions: cosmos-sdk versions <= v0.50.10, <= v0.47.14
Affected users: Chain Builders + Maintainers, Validators, node operators



### Impact

### ASA-2024-0012

When decoding a maliciously formed packet with a deeply-nested structure, it may be possible for a stack overflow to occur and result in a network halt. This was addressed by adding a recursion limit while decoding the packet.

### ASA-2024-0013

Nested messages in a transaction can consume exponential cpu and memory on `UnpackAny` calls.  The`max_tx_bytes` sets a limit for external TX but is not applied for internal messages emitted by wasm contracts or a malicious validator block. This may result in a node crashing due to resource exhaustion.  This was addressed by adding additional validation to prevent this condition.


### Patches

The issues above are resolved in Cosmos SDK versions v0.47.15 or v0.50.11.
Please upgrade ASAP.

### Timeline for ASA-2024-0012

* October 1, 2024, 12:29pm UTC: Issue reported to the Cosmos Bug Bounty program
* October 1, 2024, 2:47pm UTC: Issue triaged by Amulet on-call, and distributed to Core team

_Trimmed to 38 lines — full report: https://github.com/cosmos/cosmos-sdk/security/advisories/GHSA-8wcc-m6j2-qxvm_
