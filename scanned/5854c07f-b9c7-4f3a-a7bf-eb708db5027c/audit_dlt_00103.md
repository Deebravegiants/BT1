# [C] ISA-2025-001: Non-deterministic JSON Unmarshalling of IBC Acknowledgement can result in a chain halt

## Summary
Severity: Critical
Chain: Cosmos
Component: cosmos/ibc-go
Published: 2025-03-12
Source: https://github.com/cosmos/ibc-go/security/advisories/GHSA-4wf3-5qj9-368v
Type: github-advisory

## Details
Name: ISA-2025-001: Non-deterministic JSON Unmarshalling of IBC Acknowledgement can result in a chain halt
Component: IBC-Go
Criticality: High (Considerable Impact; Likely Likelihood per [ACMv1.2](https://github.com/interchainio/security/blob/main/resources/CLASSIFICATION_MATRIX.md))
Affected versions: IBC-Go >= v7; Earlier IBC-Go versions MAY also be affected.
Affected users: Validators, Full nodes, IBC Middleware authors

### Description

An issue was discovered in IBC-Go's deserialization of acknowledgements that results in non-deterministic behavior which can halt a chain. Any user that can open an IBC channel can introduce this state to the chain. The following patch is in addition to the previous patch which now extends the same protection to all applications beyond transfer.

### Patches

The new IBC-Go releases below address this issue:

* [v7.10.0](https://github.com/cosmos/ibc-go/releases/tag/v7.10.0)
* [v8.7.0](https://github.com/cosmos/ibc-go/releases/tag/v8.7.0)

### Workarounds

To prevent this state from being introduced to a chain, it is possible to permission Channel Opening as a workaround.

### Notes on Re-Release

This is an extension of the previous patch, please update to the latest patch to get full coverage against the reported issue.

#### Is this state breaking?

This patch is not state breaking unless an exploit is submitted before the patch is applied across the network in which case the chain will halt just as if it was unpatched. Thus, you can safely apply this patch in a rolling manner and encourage validators to patch as soon as possible in order to prevent any chain halts (and we've already cut new versions of these for you).

#### Testing we have done to gain more confidence in this release
* In addition to testing ibc-go, we also did the following:
* Tested PFM v7 and v8 after bumping dependencies
* Tested ibc-hooks v7 and v8 after bumping dependencies
* Ran a patched node on Cosmos Hub Mainnet and triggered failing and successful transactions that used PFM
* Ran a patched node on Osmosis mainnet and triggered failing and successful transactions that used ibc-hooks
This is a more thorough process than before, so we have higher confidence.

This issue was reported to the Cosmos Bug Bounty Program by swelf19 on HackerOne on February 18, 2025. If you believe you have found a bug in the Interchain Stack or would like to contribute to the program by reporting a bug, please see https://hackerone.com/cosmos.

_Trimmed to 38 lines — full report: https://github.com/cosmos/ibc-go/security/advisories/GHSA-4wf3-5qj9-368v_
