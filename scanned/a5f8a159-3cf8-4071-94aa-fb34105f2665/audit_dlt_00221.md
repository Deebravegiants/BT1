# [M] CL-2020-21: Gossip MsgID with snappy alloc blowup

## Summary
Severity: Medium
Chain: Ethereum (consensus layer)
Component: Prysm
Published: 2021-12-01
Source: https://github.com/ethereum/public-disclosures/blob/master/disclosures/CL-2021-12-01.md
Type: ef-disclosure

## Details
Affected Clients: Prysm
Uid: CL-2020-21
Bug: Gossip MsgID with snappy alloc blowup
Type: DoS
Summary: Message ID of gossip message uses Snappy block compression. Contains a varint header to define decompressed size. Unchecked in Prysm, enables a single gossip message to alloc 4 GB byte array. Which is then also hashed for message ID, if crafted to be valid.
Reported: 2020-12-09
Published: 2021-12-01
Severity: Medium
Bounty Hunter: Proto
Bounty Points: 7000
Bounty Reward (Usd): 0
