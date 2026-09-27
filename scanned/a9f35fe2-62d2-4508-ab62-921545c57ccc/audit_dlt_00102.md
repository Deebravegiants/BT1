# [H] ASA-2024-001: Validation of `VoteExtensionsEnableHeight` can cause chain halt

## Summary
Severity: High
Chain: Cosmos
Component: cometbft/cometbft
Published: 2024-01-18
Source: https://github.com/cometbft/cometbft/security/advisories/GHSA-qr8r-m495-7hc4
Type: github-advisory

## Details
**Component:** CometBFT
**Criticality:** High
**Affected versions:** >= 0.38.x, main development
**Affected users:** Chain Builders + Maintainers, Validators

## Summary

A vulnerability in CometBFT’s validation logic for `VoteExtensionsEnableHeight` can result in a chain halt when triggered through a governance parameter change proposal on an ABCI2 Application Chain. If a parameter change proposal including a `VoteExtensionsEnableHeight` modification is passed, nodes running the affected versions may panic, halting the network.

The CometBFT team addressed this issue by improving validation logic for the `VoteExtensionsEnableHeight` to correctly handle governance proposals addressing this parameter.

## Next Steps for Impacted Parties

If you are a chain developer with an active network running on CometBFT v. 0.38.x, we recommend updating your chain application to v0.38.3 or later of CometBFT to patch this issue. 

This issue can be resolved with a “soft patch” to an active network, i.e. nodes can be patched and restarted at different times without the need for a coordinated upgrade that halts a chain. If this patching methodology is used, the risk of a network halt triggered by this issue is mitigated once more than 66.7% of voting power on the network has applied the update, which provides protection from exploitation while on-chain governance processes for software upgrades take place. Once all validator nodes operating a network have been updated, the risk of a network halt due to this issue will be fully resolved. 



For more information about CometBFT, see https://docs.cometbft.com/. 

This issue was found by Dongsam ([@b_harvest](https://twitter.com/b__harvest?lang=en)) who reported it to the Cosmos Bug Bounty Program on HackerOne on January 15, 2024. If you believe you have found a bug in the Interchain Stack or would like to contribute to the program by reporting a bug, please see https://hackerone.com/cosmos.
