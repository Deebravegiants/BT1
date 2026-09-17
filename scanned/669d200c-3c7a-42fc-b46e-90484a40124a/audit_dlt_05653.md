# [?] `TestStatusRPCRequest_FinalizedBlockSkippedSlots`:  Avoid panic if the stream handler is invoked more than once, by avoiding `wg.Done` to lead to a ne

## Summary
Severity: Unknown
Chain: Ethereum
Component: prysmaticlabs/prysm
Published: 2026-07-19
Source: https://github.com/OffchainLabs/prysm/commit/81c5fc9bc6504b056a95dd6ede737419ca9a4a12
Type: security-commit

## Details
`TestStatusRPCRequest_FinalizedBlockSkippedSlots`:  Avoid panic if the stream handler is invoked more than once, by avoiding `wg.Done` to lead to a negative counter. (#17197)

**What type of PR is this?**
Other

**What does this PR do? Why is it needed?**
Before this PR, `TestStatusRPCRequest_FinalizedBlockSkippedSlots` may
panic if the stream handler is invoked more than once (e.g. a duplicate
stream on the connection).

`wg.Done` is called too many times, leading to a panic caused by a
negative wait group counter.

This PR ensures that `wg.Done` is called at most once.

**Acknowledgements**

- [x] I have read
[CONTRIBUTING.md](https://github.com/prysmaticlabs/prysm/blob/develop/CONTRIBUTING.md).
- [x] I have included a uniquely named [changelog fragment
file](https://github.com/prysmaticlabs/prysm/blob/develop/CONTRIBUTING.md#maintaining-changelogmd).
- [x] I have added a description with sufficient context for reviewers
to understand this PR.
- [x] I have tested that my changes work as expected and I added a
testing plan to the PR description (if applicable).
