# [M] Rabby incident: DeBank plug-in wallet Rabby tweeted that its Rabby Swap smart contract has a vulnerability, and users who have used it should revo

## Summary
Severity: Medium
Target: Rabby
Loss: $ 190,000
Attack method: Contract Vulnerability
Published: 2022-10-11
Source: https://twitter.com/SlowMist_Team/status/1579839744128978945
Type: slowmist-incident

## Details
DeBank plug-in wallet Rabby tweeted that its Rabby Swap smart contract has a vulnerability, and users who have used it should revoke Rabby Swap approvals on all chains as soon as possible. According to the analysis of the SlowMist security team, the Rabby Swap contract was attacked, and the token exchange function in the contract was directly called externally through the functionCallWithValue function in the OpenZeppelin Address library. The parameters passed in by the user are not checked, resulting in any external call problems. Attackers exploit this issue to steal funds from users authorized by this contract.
