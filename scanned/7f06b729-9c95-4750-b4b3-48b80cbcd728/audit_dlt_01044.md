# [M] Tendermint Core vulnerable to Uncontrolled Resource Consumption

## Summary
Severity: Medium
Chain: github.com/tendermint/tendermint
Component: github.com/tendermint/tendermint
CVE: CVE-2021-21271
CWE: Uncontrolled Resource Consumption
Published: 2022-10-07
Source: https://github.com/advisories/GHSA-p658-8693-mhvg
Type: github-advisory

## Details
### Description 

Tendermint Core v0.34.0 introduced a new way of handling evidence of misbehavior. As part of this, [we added a new `Timestamp` field to `Evidence` structs](https://github.com/tendermint/tendermint/pull/5219). This timestamp would be calculated using the same algorithm that is used when a block is created and proposed. (This algorithm relies on the timestamp of the last commit from this specific block.) 

In Tendermint Core v0.34.0-v0.34.2, the `consensus` reactor is responsible for forming `DuplicateVoteEvidence` whenever double signs are observed. However, the current block is still “in flight” when it is being formed by the `consensus` reactor. It hasn’t been finalized through network consensus yet. This means that different nodes in the network may observe different “last commits” when assigning a timestamp to `DuplicateVoteEvidence.`

In turn, different nodes could form `DuplicateVoteEvidence` objects at the same height but with different timestamps. One `DuplicateVoteEvidence` object (with one timestamp) will then eventually get finalized in the block, but this means that any `DuplicateVoteEvidence` with a different timestamp is considered invalid. Any node that formed invalid `DuplicateVoteEvidence` will continue to propose invalid evidence; its peers may see this, and choose to disconnect from this node. This bug means that double signs are DoS vectors in Tendermint Core v0.34.0-v0.34.2. 

Tendermint Core v0.34.3 is a security release which fixes this bug. As of v0.34.3, `DuplicateVoteEvidence` is no longer formed by the `consensus` reactor; rather, the `consensus` reactor passes the `Vote`s themselves into the `EvidencePool`, which is now responsible for forming `DuplicateVoteEvidence`. The `EvidencePool` has timestamp info that should be consistent across the network, which means that `DuplicateVoteEvidence` formed in this reactor should have consistent timestamps. 

This release changes the API between the `consensus` and `evidence` reactors. 

### Impact

This is a denial-of-service vector which impacts networks running Tendermint Core v0.34.0 - v0.34.2.

### Remediation

This problem has been patched in Tendermint Core v0.34.3. Networks running impacted versions of Tendermint Core should update immediately.

### Workarounds

There are no workarounds, other than upgrading to a patched version of Tendermint Core.

### Credits 

* Crypto.com (@cyril-crypto, @brianatcrypto, @tomtau and  @yihuang) for finding and submitting this vulnerability
* @melekes and @cmwaters for identifying the root cause and patching the problem 

### For more information

If you have any questions or comments about this advisory:
* Open an issue in [tendermint/tendermint](https://github.com/tendermint/tendermint)
* Email us at [security@tendermint.com](mailto:security@tendermint.com)
