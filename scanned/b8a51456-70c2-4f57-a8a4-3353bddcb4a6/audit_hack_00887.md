# [M] Avalanche incident: On February 23rd, the Avalanche mainnet experienced block production interruptions. Addressing this issue, Ava Labs co-founder Kev

## Summary
Severity: Medium
Target: Avalanche
Loss: -
Attack method: Security Vulnerability
Published: 2024-02-23
Source: https://twitter.com/_patrickogrady/status/1761057598143643696
Type: slowmist-incident

## Details
On February 23rd, the Avalanche mainnet experienced block production interruptions. Addressing this issue, Ava Labs co-founder Kevin Sekniqi stated on Twitter that the problem appears to be a gossip-related mempool management error, which is purely a code-related issue, not a performance handling problem. It seems that inscriptions have reached an edge case, but they did not affect performance. The mainnet downtime issue appears to be related to an edge-case bug in mempool processing, and bug fix testing is currently underway on the Avalanche testnet. On February 24th, Ava Labs engineering lead Patrick O'Grady tweeted that nodes need to be upgraded to AvalancheGo version 1.11.1, which disables the logic added in v1.10.18 that caused validators to send excessive amounts of gossip to each other. Avalanche Validators provision a stake-weighted bandwidth allocation for each peer, and this flawed logic led each node to saturate their allocation with useless transaction gossip. This dynamic prevented pull queries issued by validators from being processed in a timely manner and resulted in consensus stalling.
