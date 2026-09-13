# [M] Squid Multicall incident: A user mistakenly approved the SquidMulticall contract (instead of the intended Squid Router contract) with unlimited token allowa

## Summary
Severity: Medium
Target: Squid Multicall
Loss: $ 517,000
Attack method: Approval Exploit
Published: 2026-04-07
Source: https://blocksec.com/blog/weekly-web3-security-incident-roundup-apr-6-apr-12-2026
Type: slowmist-incident

## Details
A user mistakenly approved the SquidMulticall contract (instead of the intended Squid Router contract) with unlimited token allowances. An attacker then called the permissionless run() function on SquidMulticall with crafted calldata to execute transferFrom() from the victim’s approved tokens across multiple chains (ETH, BSC, Arbitrum, Avalanche, etc.). This drained approximately $517K.
