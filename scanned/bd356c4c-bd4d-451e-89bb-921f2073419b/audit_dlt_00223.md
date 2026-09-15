# [M] CL-2020-23: Forkchoice selfish mining alike attack

## Summary
Severity: Medium
Chain: Ethereum (consensus layer)
Component: Spec
Published: 2021-12-01
Source: https://github.com/ethereum/public-disclosures/blob/master/disclosures/CL-2021-12-01.md
Type: ef-disclosure

## Details
Affected Clients: Spec
Uid: CL-2020-23
Bug: Forkchoice selfish mining alike attack
Type: Forkchoice
Summary: Due to the fork choice being rooted on a block graph, rather than a (block, slot) graph, an attacker can withhold blocks and some attestations until after committee voting on (empy) and subsequent blocks/slots to purposefully oprhan proposals. When 30%+ cartel, they can cause finality delays with non-trivial probability.
Reported: 2020-12-11
Published: 2021-12-01
Severity: Medium
Bounty Hunter: WINE Academic Workshop
Bounty Points: 0
Bounty Reward (Usd): 0
