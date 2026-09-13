# [H] ISA-2025-002: x/group can halt when erroring in EndBlocker

## Summary
Severity: High
Chain: Cosmos
Component: cosmos/cosmos-sdk
Published: 2025-03-12
Source: https://github.com/cosmos/cosmos-sdk/security/advisories/GHSA-47ww-ff84-4jrg
Type: github-advisory

## Details
Name: ISA-2025-002: x/group can halt when erroring in EndBlocker
Component: CosmosSDK
Criticality: High (Considerable Impact; Likely Likelihood per [ACMv1.2](https://github.com/interchainio/security/blob/main/resources/CLASSIFICATION_MATRIX.md))
Affected versions: <= v0.47.16, <= 0.50.12
Affected users: Validators, Full nodes, Users on chains that utilize the groups module
Cosmos SDK chains in unpatched releases that use the `x/group` module are affected.

### Description

An issue was discovered in the groups module where malicious proposals would result in an errors triggered in the module's end blocker that could result in a chain halt.  Any set of users that can interact with the groups module could introduce this state.

### Patches
_Has the problem been patched? What versions should users upgrade to?_

The new Cosmos SDK release [v0.50.13](https://github.com/cosmos/cosmos-sdk/releases/tag/v0.50.13) and [v0.47.17](https://github.com/cosmos/cosmos-sdk/releases/tag/v0.47.17) fix this issue.

### Testing

Testing we have done to gain more confidence in this release:

In addition to testing Cosmos SDK we also did the following:

- Ran a patched node in a local `v0.50` testnet with the failing state and did not halt (an unpatched network confirmed to halt)
- Ran a patched node on Xion Mainnet (uses `x/group`)
- Ran a patched node on Zetachain Mainnet (uses `x/xgroup`)
    
### Workarounds
_Is there a way for users to fix or remediate the vulnerability without upgrading?_

There are no known workarounds for this issue. It is advised that chains apply the update.

This issue was reported to the Cosmos Bug Bounty Program by [wbowling](https://github.com/wbowling) on HackerOne on February 28, 2025. If you believe you have found a bug in the Interchain Stack or would like to contribute to the program by reporting a bug, please see https://hackerone.com/cosmos.

If you have questions about Interchain security efforts, please reach out to our official communication channel at [security@interchain.io](mailto:security@interchain.io). For more information about the Interchain Foundation’s engagement with Amulet, and to sign up for security notification emails, please see https://github.com/interchainio/security.
