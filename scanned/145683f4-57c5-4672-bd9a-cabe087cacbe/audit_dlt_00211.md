# [H] CL-2020-06: DoS Attack due to Discv5 spec

## Summary
Severity: High
Chain: Ethereum (consensus layer)
Component: All clients
Published: 2021-12-01
Source: https://hackmd.io/Bmq\_GlVXQtu3Z-YfVVFioA?view
Type: ef-disclosure

## Details
Affected Clients: All clients
Uid: CL-2020-06
Bug: DoS Attack due to Discv5 spec
Type: DoS
Summary: A DoS attack that exploits an RLP ecoding error (and lack of packet size validation) that eventually causes client crash and reply with a flood of WHOAREYOU messages that are larger than the attackers message.
Links: [https://hackmd.io/Bmq\_GlVXQtu3Z-YfVVFioA?view](https://hackmd.io/Bmq_GlVXQtu3Z-YfVVFioA?view)
Reported: 2020-08-25
Fixed Date: 2020-10-07
Published: 2021-12-01
Severity: High
Bounty Hunter: Jonny Rhea
Bounty Points: 5000
Bounty Reward (Usd): 10000
