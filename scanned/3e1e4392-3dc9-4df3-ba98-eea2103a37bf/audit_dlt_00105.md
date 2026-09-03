# [C] ASA-2024-007: Potential Reentrancy using Timeout Callbacks in ibc-hooks

## Summary
Severity: Critical
Chain: Cosmos
Component: cosmos/ibc-go
CWE: Incorrect Behavior Order
Published: 2024-04-05
Source: https://github.com/cosmos/ibc-go/security/advisories/GHSA-j496-crgh-34mx
Type: github-advisory

## Details
**Name**: ASA-2024-007: Potential Reentrancy using Timeout Callbacks in ibc-hooks
**Component**: ibc-go
**Criticality**: Critical ([ACMv1](https://github.com/interchainio/security/blob/main/resources/CLASSIFICATION_MATRIX.md): I:Critical; L:AlmostCertain)
**Affected versions**: < v4.6.0, < v5.4.0, < v6.3.0, < v7.4.0, < v8.2.0
**Affected users**: Chain Builders + Maintainers

# Summary

Through the deployment and subsequent use of a malicious CosmWasm contract via IBC interactions, an attacker could potentially execute the same `MsgTimeout` inside the IBC hook for the `OnTimeout` callback before the packet commitment is deleted. On chains where ibc-hooks wraps ICS-20, this vulnerability may allow for the logic of the `OnTimeout` callback of the transfer application to be recursively executed, leading to a condition that may present the opportunity for the loss of funds from the escrow account or unexpected minting of tokens.

# Affected Configurations

Chains which satisfy all of the following requirements are considered to be impacted by this vulnerability:
* Chain is IBC-enabled and uses a vulnerable version of ibc-go
* Chain is CosmWasm-enabled and allows code uploads for wasm contracts by anyone, or by authorized parties (to a lesser extent)
* Chain utilizes the ibc-hooks middleware and wraps ICS-20 transfer application

# Next Steps for Impacted Chain Builders and Maintainers

It is advised to immediately upgrade to the latest patch fix version of ibc-go for your chain. If you have already applied a soft-patch through private coordination, we recommend additionally updating to the latest ibc-go version via normal software upgrade governance.

If you have not upgraded your chain yet, and you desire to mitigate exposure to this vulnerability in the meantime, it is advisable to limit code uploading for contracts to trusted parties on your chain.

**If your chain only allows permissioned, access-controlled contract uploads, it is still strongly recommended to update to the latest patched ibc-go version for your chain per your normal software upgrade process.**

# Preparing for future coordination

If your chain would like to be included in future coordination efforts, please ensure your chain has a prominently displayed or otherwise easily available up-to-date email address for technical security contact available. A security.md file in the root of your projects’ code repository should contain this information. Additionally, please test this security contact with an unaffiliated email to ensure it works as expected and can receive emails from outside of your domain.

To ensure that your chain is included in future impact assessments, please keep your chain information up to date in the [Cosmos Chain Registry](https://github.com/cosmos/chain-registry) with code location, network name, and public RPC and API endpoints in the details.

We recommend that all chains configure and practice the use of the [Circuit Breaker module](https://docs.cosmos.network/main/build/modules/circuit) in the Cosmos SDK, as future vulnerability notifications may require the use of this mechanism as a mitigation against exploitation.

# Recognition

This issue was reported to the Cosmos Bug Bounty Program on HackerOne on 3/26/24 by Maxwell Dulin (@mdulin2) at [Asymmetric Research](https://www.asymmetric.re/). If you believe you have found a bug in the Interchain Stack or would like to contribute to the program by reporting a bug, please see https://hackerone.com/cosmos.

# Notes

_Trimmed to 38 lines — full report: https://github.com/cosmos/ibc-go/security/advisories/GHSA-j496-crgh-34mx_
