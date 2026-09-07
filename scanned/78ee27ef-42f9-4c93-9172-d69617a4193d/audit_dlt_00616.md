# [?] fix: prevent duplicate aggregates passing validation due to race condition (#8716)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ChainSafe/lodestar
Published: 2025-12-31
Source: https://github.com/ChainSafe/lodestar/commit/ae3f082e014762f6d44e4e271f8f69755041bc1b
Type: security-commit

## Details
fix: prevent duplicate aggregates passing validation due to race condition (#8716)

**Motivation**


https://github.com/ChainSafe/lodestar/pull/8711#pullrequestreview-3612431091

**Description**

Prevent duplicate aggregates passing gossip validation due to race
condition by checking again if we've seen the aggregate before inserting
it into op pool. This is required since we run multiple async operations
in-between first check and inserting it into op pool.


<img width="942" height="301" alt="image"
src="https://github.com/user-attachments/assets/2701a92e-7733-4de3-bf4a-ac853fd5c0b7"
/>

`AlreadyKnown` disappears since we now filter those out properly during
gossip validation which is important since we don't wanna re-gossip
those aggregates.
