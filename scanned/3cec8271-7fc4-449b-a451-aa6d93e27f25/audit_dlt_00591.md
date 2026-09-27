# [?] Fix issue : Prevent makeslice panic from invalid Count values (#16227)

## Summary
Severity: Unknown
Chain: Ethereum
Component: prysmaticlabs/prysm
Published: 2026-01-16
Source: https://github.com/OffchainLabs/prysm/commit/a135a336c37d11883e9fc72e44f698339b18043b
Type: security-commit

## Details
Fix issue : Prevent makeslice panic from invalid Count values (#16227)

**What type of PR is this?**

Bug fix

**What does this PR do? Why is it needed?**

Add defensive checks to prevent panic from large Count values that could
result from unsigned integer underflow:

1. In batch.blockRequest() and batch.blobRequest(): Return Count=0 when
end <= begin, preventing the underflow at the source.

2. In SendBeaconBlocksByRangeRequest(): Cap slice capacity to
MaxRequestBlock before allocation to prevent panic even if upstream code
produces invalid values.


**Which issues(s) does this PR fix?**

Fixes #16223

**Other notes for review**

**Acknowledgements**

- [x] I have read
[CONTRIBUTING.md](https://github.com/prysmaticlabs/prysm/blob/develop/CONTRIBUTING.md).
- [x] I have included a uniquely named [changelog fragment
file](https://github.com/prysmaticlabs/prysm/blob/develop/CONTRIBUTING.md#maintaining-changelogmd).
- [x] I have added a description with sufficient context for reviewers
to understand this PR.
- [x] I have tested that my changes work as expected and I added a
testing plan to the PR description (if applicable).
