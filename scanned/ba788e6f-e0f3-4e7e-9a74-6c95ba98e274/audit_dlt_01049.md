# [M] Denial of Service in TenderMint

## Summary
Severity: Medium
Chain: github.com/tendermint/tendermint
Component: github.com/tendermint/tendermint
CVE: CVE-2020-15091
CWE: Improper Verification of Cryptographic Signature
Published: 2021-12-20
Source: https://github.com/advisories/GHSA-6jqj-f58p-mrw3
Type: github-advisory

## Details
### Description

**Denial of Service**

Tendermint 0.33.0 and above allow block proposers to include signatures for the wrong block. This may happen naturally if you start a network, have it run for some time and restart it without changing the chainID. (It is a [misconfiguration](https://docs.tendermint.com/master/tendermint-core/using-tendermint.html) to reuse chainIDs.) Correct block proposers will accidentally include signatures for the wrong block if they see these signatures, and then commits won't validate, making all proposed blocks invalid. A malicious validator (even with a minimal amount of stake) can use this vulnerability to completely halt the network.

Tendermint 0.33.6 checks all the signatures are for the block with +2/3 majority before creating a commit.

**False Witness**

Tendermint 0.33.1 and above are no longer fully verifying commit signatures during block execution - they stop after +2/3. This means proposers can propose blocks that contain valid +2/3 signatures and then the rest of the signatures can be whatever they want. They can claim that all the other validators signed just by including a CommitSig with arbitrary signature data. While this doesn't seem to impact safety of Tendermint per se, it means that Commits may contain a lot of invalid data **.

_** This was already true of blocks, since they could include invalid txs filled with garbage, but in that case the application knew that they are invalid and could punish the proposer. But since applications didn't--and don't-- verify commit signatures directly (they trust Tendermint to do that), they won't be able to detect it._

This can impact incentivization logic in the application that depends on the LastCommitInfo sent in BeginBlock, which includes which validators signed. For instance, Gaia incentivizes proposers with a bonus for including more than +2/3 of the signatures. But a proposer can now claim that bonus just by including arbitrary data for the final -1/3 of validators without actually waiting for their signatures. There may be other tricks that can be played because of this.

Tendermint 0.33.6 verifies all the signatures during block execution ***.

_*** Please note that the light client does not check nil votes and exits as soon as 2/3+ of the signatures are checked._

### Impact

- All nodes
- The network stops due to having a commit with a wrong signature.

### Patches

- v0.33.6 andn v0.34.0-dev1.0.20200702134149-480b995a3172

### Workarounds

No workarounds.

### References

- https://github.com/tendermint/tendermint/issues/4926

### For more information

_Trimmed to 38 lines — full report: https://github.com/advisories/GHSA-6jqj-f58p-mrw3_
