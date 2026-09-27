# [C] Qubit incident: Qubit, the lending product of QBridge, a BSC ecological decentralized lending project, is suspected to have been hacked. The hacke

## Summary
Severity: Critical
Target: Qubit
Loss: $ 80,000,000
Attack method: Contract Vulnerability
Published: 2022-01-28
Source: https://medium.com/@QubitFin/protocol-exploit-report-305c34540fa3
Type: slowmist-incident

## Details
Qubit, the lending product of QBridge, a BSC ecological decentralized lending project, is suspected to have been hacked. The hackers minted a large amount of xETH collateral and consumed about $80 million in assets in the capital pool. According to SlowMist's analysis, the main reason for this attack is that when the recharge of ordinary tokens and native tokens are implemented separately, when transferring the tokens in the whitelist, it is not checked again whether they are 0 addresses, resulting in The operation that should be recharged through the native recharge function can successfully go through the recharge logic of ordinary tokens.
