# [M] CL-2020-24: Forkchoice proto-array delayed head update edge-case

## Summary
Severity: Medium
Chain: Ethereum (consensus layer)
Component: All clients
Published: 2021-12-01
Source: https://github.com/ethereum/public-disclosures/blob/master/disclosures/CL-2021-12-01.md
Type: ef-disclosure

## Details
Affected Clients: All clients
Uid: CL-2020-24
Bug: Forkchoice proto-array delayed head update edge-case
Type: Forkchoice
Summary: The original proto-array algo did two sweeps: one to update weights, one to update node relations (calculating the new head). The translated version only does 1 sweep, combining the two.<br><br>In a situation where lots of votes move to a different fork, this causes the weights to update after the node relations, leaving the proto-array with consistent weights, but invalid node relations. Thus left with the old (now incorrect) head.<br><br>The next sweep resolves it, and should be within a slot. Exploiting this within a slot may be possible on epoch boundary, but requires a significant split in forkchoice votes between two contending splits, or a significant amount of votes.
Reported: 2020-12-11
Published: 2021-12-01
Severity: Medium
Bounty Hunter: Saulius Grigaitis (+team).
Bounty Points: 9000
Bounty Reward (Usd): 18000
