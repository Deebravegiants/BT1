# [M] CL-2020-22: Gossip message cache OOM

## Summary
Severity: Medium
Chain: Ethereum (consensus layer)
Component: Lighthouse
Published: 2021-12-01
Source: https://github.com/ethereum/public-disclosures/blob/master/disclosures/CL-2021-12-01.md
Type: ef-disclosure

## Details
Affected Clients: Lighthouse
Uid: CL-2020-22
Bug: Gossip message cache OOM
Type: DoS
Summary: Rust libp2p puts message in cache before user-validation. Crafting ~10 byte messages that decompress to 80x or more is possible. Now use the unbounded publish list to put 100k messages in a single 1 MB gossip RPC container. The messages stay in the cache for 6 heartbeats (4.7 seconds). Send ~12 crafted 1 MB messages in that window for a 1 GB memory spike.
Reported: 2020-12-10
Published: 2021-12-01
Severity: Medium
Bounty Hunter: Proto
Bounty Points: 7000
Bounty Reward (Usd): 0
