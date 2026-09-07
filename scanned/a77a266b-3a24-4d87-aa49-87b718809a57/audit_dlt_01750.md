# [?] fix: panic on new if trie_state_resharder in progress (#13719)

## Summary
Severity: Unknown
Chain: NEAR
Component: near/nearcore
Published: 2025-06-19
Source: https://github.com/near/nearcore/commit/f7430bce6353fd8063fcf9598dc734de18aca91f
Type: security-commit

## Details
fix: panic on new if trie_state_resharder in progress (#13719)

The goal of this PR is to prevent the node from starting operations if
the resharding was started but not completed, so it would be obvious to
the node operator that they need to run the resharding resume command.

An alternative could be to check for this in an initialization path more
explicitly like Chain::new for example.
This seems more contained.
