# [M] CL-2021-15: Prysm missing state root check

## Summary
Severity: Medium
Chain: Ethereum (consensus layer)
Component: Prysm
Published: 2021-12-01
Source: https://github.com/ethereum/public-disclosures/blob/master/disclosures/CL-2021-12-01.md
Type: ef-disclosure

## Details
Affected Clients: Prysm
Uid: CL-2021-15
Bug: Prysm missing state root check
Type: Bug
Summary: Prysm checks the state root in the transition function that is used by tests, but uses a different transition function during sync and gossip block handling, that missed the validation of the state-root. The function was a "no verify version" that would return a signature set for batch-verification outside of the function, but did not defer the state-root check in the same way. This makes the state-root effectively a graffiti field. The state-transition ignores the state-root when inserting the latest-header, but the block-root is still affected. This causes prysm to run into a bad block, store the resulting hot state with the bad block-root as key, and not find the state in the DB when someone builds a block with a parent-root based on the root of the latest-header of the latest state. The damage is limited because the chain cannot grow beyond one bad block, since the header-validation of the next block would fail against the state, which has a state-root in the header with deferred computation in the start of the next slot, which was still correct.
Reported: 2021-04-07
Published: 2021-12-01
Severity: Medium
Bounty Hunter: Proto
Bounty Reward (Usd): 0
