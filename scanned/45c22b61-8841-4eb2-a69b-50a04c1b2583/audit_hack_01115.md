# [C] MEV Bots incident: On April 3, MEV bots suffered a malicious sandwich attack that cost them around $25 million. Data on the chain shows that the mali

## Summary
Severity: Critical
Target: MEV Bots
Loss: $ 25,000,000
Attack method: Sandwich Attack
Published: 2023-04-03
Source: https://www.panewslab.com/zh/sqarticledetails/yov8heci.html
Type: slowmist-incident

## Details
On April 3, MEV bots suffered a malicious sandwich attack that cost them around $25 million. Data on the chain shows that the malicious verifier who attacked the MEV bots today has been punished by Slash and kicked out of the verifier queue. According to SlowMist analysis, the reason why the MEV bots was attacked was that even if the beacon block was incorrect, the relay still returned the payload to the proposer, which resulted in the proposer being able to access the content of the block before another block was finalized. The attacker takes advantage of this problem to maliciously construct an invalid block, so that the block cannot be verified, and the relay cannot broadcast (the status code is 202) to obtain the transaction content in advance. mev-boost-relay has urgently released a new version to alleviate this problem, and it is recommended that relay operators upgrade the relay in time.
